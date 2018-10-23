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
        return render(request, "blog/blog_dashboard.html", {
            "posts": Post.objects.all()
        })

    def post(self, request):
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
        return render(request, "blog/blog_index.html", {
            "posts": Post.objects.all().exclude(published=False)
        })


class PostCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = PostForm()
        return render(request, "blog/create_blog.html", {
            "form": form,
        })

    def post(self, request):
        print(request.FILES)
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
        post = Post.objects.get(pk=pk)
        form = PostForm(instance=post)
        return render(request, "blog/edit_blog.html", {
            "form": form,
        })

    def post(self, request, pk):
        post = Post.objects.get(pk=pk)
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
        try:
            post = Post.objects.get(pk=pk)
            post.views += 1
            post.save()
            copied_post = deepcopy(post)
            # this is so that the html is displayed with quotes correctly, without
            # modifying the text that Donut writes so he can still edit it
            while "```" in copied_post.content:
                start = copied_post.content.index("```")
                end = copied_post.content.index("```", start + 1)
                quote = copied_post.content[start + 3: end]
                while "<p>" in quote:
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
