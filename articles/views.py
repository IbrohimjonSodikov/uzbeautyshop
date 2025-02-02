from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.shortcuts import redirect
from .models import Article, Comment
from django.utils.translation import gettext as _
from django.utils import translation

class ArticleListView(ListView):
    model = Article
    template_name = 'article_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_language = translation.get_language()

        # Update the articles in context with the correct language fields
        for article in context['object_list']:
            if user_language == 'ru':
                article.title = article.title_ru
                article.summary = article.summary_ru
            elif user_language == 'uz':
                article.title = article.title_uz
                article.summary = article.summary_uz
            else:
                article.title = article.title
                article.summary = article.summary

        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        user_language = translation.get_language()

        # Set the appropriate content based on the language
        if user_language == 'ru':
            context['title'] = article.title_ru
            context['body'] = article.body_ru
        elif user_language == 'uz':
            context['title'] = article.title_uz
            context['body'] = article.body_uz
        else:
            context['title'] = article.title
            context['body'] = article.body

        return context

    def post(self, request, *args, **kwargs):
        article = self.get_object()
        comment_body = request.POST.get('comment')

        if comment_body:
            Comment.objects.create(
                article=article,
                author=request.user,
                body=comment_body
            )

        return redirect('article_detail', pk=article.pk)


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class ArticleUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Article
    fields = ('title', 'summary', 'body', 'photo',)
    template_name = 'article_edit.html'

class ArticleDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Article
    template_name = 'article_delete.html'
    success_url = reverse_lazy('article_list')

class ArticleCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Article
    template_name = 'article_new.html'
    fields = ('title', 'summary', 'body', 'photo',)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
