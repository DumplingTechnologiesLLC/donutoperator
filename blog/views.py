from copy import deepcopy
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.views import View
from blog.models import Post
from filebrowser.sites import site
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.forms import PostForm
from django.shortcuts import render
site.directory = "uploads/"


class PostDashboard(LoginRequiredMixin, View):
    def get(self, request):
        """Returns the dashboard for admins to manage blog posts.

        Arguments:
        :param request: A WSGI Django request

        Returns:
        a render of blog_dashboard with all posts ordered by date of creation
        """
        return render(request, "blog/blog_dashboard.html", {
            "posts": Post.objects.all().order_by("created")
        })

    def post(self, request):
        """Performs multiple different actions based on the method chosen.

        Each method includes a variety of parameters described below
        method - delete
            Arguments:
            pk -  the primary key of an article to be deleted

            Returns:
                on success:
                    a message stating "Article deleted successfully"

                on failure:
                    a message stating "We couldn't find that article in the database."

        method - publish
            Arguments:
            pk - the primary key of an article to be published or unpublished
            if the article already is published

            Returns:
                on success:
                    a message stating "Article taken down from public view successfully."
                    or "Article published successfully."

                on failure:
                    a message stating "We couldn't find that article in the database."

        Arguments:
        :param request: A WSGI Django request with different POST dictionaries, but
        always will include a method with a string value that determines which action
        will take place.

        Returns:
        An HttpResponseRedirect with an appropriate message as described above.
        """
        method = request.POST.get("action")
        if method == "delete":
            pk = request.POST.get("pk")
            try:
                article = Post.objects.get(pk=pk)
                article.delete()
                messages.success(request, "Article deleted successfully")
                return HttpResponseRedirect(reverse("blog:dashboard"))
            except Post.DoesNotExist:
                messages.error(request, "We couldn't find that article in the database.")
                return HttpResponseRedirect(reverse("blog:dashboard"))
        elif method == "publish":
            pk = request.POST.get("pk")
            try:
                article = Post.objects.get(pk=pk)
                if article.published:
                    article.published = False
                    article.publish_date = None
                    article.save()
                    messages.success(
                        request, "Article taken down from public view successfully.")
                    return HttpResponseRedirect(reverse("blog:dashboard"))
                else:
                    article.published = True
                    article.publish_date = timezone.now()
                    article.save()
                    messages.success(request, "Article published successfully.")
                    return HttpResponseRedirect(reverse("blog:dashboard"))
            except Post.DoesNotExist:
                messages.error(request, "We couldn't find that article in the database.")
                return HttpResponseRedirect(reverse("blog:dashboard"))
        else:
            messages.warning(
                request, "The server had an issue. We aren't sure what happened.")
            return HttpResponseRedirect(reverse("blog:dashboard"))


class PostIndexView(View):
    def get(self, request):
        """Displays all published articles, ordered by publish date

        Arguments:
        :param request: a WSGI Django request object

        Returns:
        a render of blog_index with the data described
        """
        return render(request, "blog/blog_index.html", {
            "posts": Post.objects.all().exclude(
                published=False).order_by("-publish_date")
        })


class PostCreateView(LoginRequiredMixin, View):

    def get(self, request):
        """Displays the form to create a new article

        Arguments:
        :param request: a WSGI Django request object

        Returns:
        a render of create_blog.html with the form for creating articles
        """
        form = PostForm()
        return render(request, "blog/create_blog.html", {
            "form": form,
        })

    def post(self, request):
        """Creates a new article on successful submission

        Arguments:
        :param request: a WSGI Django request object with a POST and FILES dictionary

        Returns:
        a Redirect on successful creation, a render with the form with errors on invalid
        submission
        """
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            form.image = request.FILES.get("cover_image")
            form.save()
            messages.success(request, ("Article successfully submitted. Click publish"
                                       " to make publically available"))
            return HttpResponseRedirect(reverse("blog:dashboard"))
        else:
            messages.error(request, ("Please check the form for errors and try again."))
            return render(request, "blog/create_blog.html", {
                "form": form,
            })


class PostEditView(LoginRequiredMixin, View):

    def get(self, request, pk):
        """Returns the form for editing an article

        Arguments:
        :param request: a WSGI Django request object
        :param pk: a primary key for the news article to be edited

        Returns:
        a render of blog_edit with the form prepopulated with the selected news article
        """
        post = Post.objects.get(pk=pk)
        form = PostForm(instance=post)
        return render(request, "blog/edit_blog.html", {
            "form": form,
        })

    def post(self, request, pk):
        """Edits the news article matching the pk

        Arguments:
        :param request: a WSGI Django request object
        :param pk: a primary key for the news article to be edited

        Returns:
        a redirect to the dashboard on success, a render with the error with forms
        on failure
        """
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            messages.error(request, ("We couldn't find that post."))
            return HttpResponseRedirect(reverse("blog:dashboard"))
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save(commit=False)
            form.image = request.FILES.get("cover_image")
            form.modified = timezone.now()
            form.save()
            messages.success(request, ("Article successfully edited."))
            return HttpResponseRedirect(reverse("blog:dashboard"))
        else:
            messages.error(request, ("Please check the form for errors and try again."))
            return render(request, "blog/create_blog.html", {
                "form": form,
            })


class PostDisplayView(View):
    def get(self, request, pk):
        """Displays an article

        Since we need to be able to format block quotes without modifying the original
        version so that it can still be edited, we make a deepcopy of the object,
        format the content on the copied object, and display the copied object instead
        of the actual article.

        Each newline is in <p>, so we iterate through all content that has a triple
        backtick and create a p tag that correctly aligns the block quote instead.

        Arguments:
        :param request: a WSGI Django request object

        Returns:
        a render of blog.html with the article with formatted quotes on success,
        a redirect on failure
        """
        try:
            post = Post.objects.get(pk=pk)
            if not post.published:
                messages.error(request, "That article isn't published yet.")
                return HttpResponseRedirect(reverse("blog:blog-index"))
            post.views += 1
            post.save()
            copied_post = deepcopy(post)
            # this is so that the html is displayed with quotes correctly, without
            # modifying the text that Donut writes so he can still edit it
            while "```" in copied_post.content:
                start = copied_post.content.index("```")
                end = copied_post.content.index("```", start + 1)
                quote = copied_post.content[start + 3: end]
                while "<p>" in quote:  # pragma: no cover
                    start_of_p = quote.index("<p>")
                    prior_to_p = quote[:start_of_p]
                    try:
                    	end_of_p = quote.index("</p>", start_of_p)
                    except ValueError:
                    	break
                    after_p = quote[end_of_p:]
                    inner_quote = quote[start_of_p + 3: end_of_p]
                    quote = prior_to_p + '<p style="display:flex; justify-content:center; align-items:center; font-style:italic">' + \
                        inner_quote + after_p
                prior_to_quote = copied_post.content[0:start - 3]
                after_quote = copied_post.content[end + 3:]
                prior_to_quote = prior_to_quote[0:-1] + \
                    '<p style="display:flex; justify-content:center; align-items:center; font-style:italic">'
                copied_post.content = prior_to_quote + quote + after_quote
        except Post.DoesNotExist:
            messages.error(request, "That article no longer exists.")
            return HttpResponseRedirect(reverse("blog:blog-index"))
        return render(request, "blog/blog.html", {
            "instance": copied_post,
            "posts": Post.objects.all().exclude(pk=post.id)
        })
