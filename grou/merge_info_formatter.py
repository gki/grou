# -*- coding: utf-8 -*-
"""Formatter classes and their factory class."""
from builtins import super
from common import Mode, ReviewNumPlace
from abc import ABCMeta, abstractmethod


class OutputFomatterFactory():
    """Create suitable formatter for style."""

    @classmethod
    def create(cls, style_name):
        """Create suitable formatter for style."""
        if style_name == Mode.md.name:
            return MarkdownOutputFormatter()
        elif style_name == Mode.html.name:
            return HtmlOutputFormatter()
        else:
            raise ValueError('Unexpected style: ' + style_name)


class AbstractOutputFormatter():
    """Abstract class for formatter."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def create_section_title(self, purpose_name):
        """Raw string for section title."""
        pass

    @abstractmethod
    def create_list_start(self):
        """Raw string for the start of list."""
        pass

    @abstractmethod
    def create_list_end(self):
        """Raw string for the end of list."""
        pass

    @abstractmethod
    def create_list(self, info, options):
        """Raw string for a list."""
        pass

    def put_review_num(self, show_review_num_name, texts, review_num_texts):
        """Insert or append review number and link."""
        if show_review_num_name == ReviewNumPlace.head.name:
            texts.insert(1, ''.join(review_num_texts))
        elif show_review_num_name == ReviewNumPlace.tail.name:
            texts.extend(review_num_texts)

        return texts


class MarkdownOutputFormatter(AbstractOutputFormatter):
    """Formatter class for Markdown style."""

    def create_section_title(self, purpose_name):
        """See super class description."""
        return '# ' + purpose_name

    def create_list_start(self):
        """See super class description."""
        return ''

    def create_list_end(self):
        """See super class description."""
        return '\n'

    def create_list(self, info, options):
        """See super class description."""
        texts = []
        review_num_texts = []

        texts.append('-')

        if options.no_hash is False:
            texts.append(' `{0.commit}`'.format(info))

        texts.append(' {0.body}'.format(info))

        if options.no_auther is False:
            texts.append(' by {0.auther}'.format(info))

        # create review number and link
        review_num_texts.append(' [PR{0.review_num}]'.format(info))
        if options.no_link is False:
            review_num_texts.append('({0.review_url})'.format(info))
        # put review number at the suitable index of texts.
        texts = super().put_review_num(options.show_review_num,
                                       texts,
                                       review_num_texts)
        return ''.join(texts)


class HtmlOutputFormatter(AbstractOutputFormatter):
    """Formatter class for HTML style."""

    def create_section_title(self, purpose_name):
        """See super class description."""
        return '<h1>' + purpose_name + '</h1>'

    def create_list_start(self):
        """See super class description."""
        return '<ul>'

    def create_list_end(self):
        """See super class description."""
        return '</ul>'

    def create_list(self, info, options):
        """See super class description."""
        texts = []
        review_num_texts = []

        texts.append('<li>')
        if options.no_hash is False:
            texts.append(' <code>{0.commit}</code>'.format(info))
        texts.append(' {0.body}'.format(info))
        if options.no_auther is False:
            texts.append(' by {0.auther}'.format(info))

        # create review number and link
        if options.no_link is False:
            review_num_texts.append('<a href="{0.review_url}">'.format(info))
        review_num_texts.append('PR{0.review_num}'.format(info))
        if options.no_link is False:
            review_num_texts.append('</a>'.format(info))
        texts.append('</li>')

        # put review number at the suitable index of texts.
        texts = super().put_review_num(options.show_review_num,
                                       texts,
                                       review_num_texts)
        return ''.join(texts)
