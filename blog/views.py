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
        except Post.DoesNotExist:
            messages.error(request, "That article no longer exists.")
            return HttpResponseRedirect(reverse("blog:blog-index"))
        return render(request, "blog/blog.html", {
            "instance": post,
            "posts": Post.objects.all().exclude(pk=post.id)
        })
