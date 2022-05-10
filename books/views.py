from django.db.models import Q

from rest_framework import exceptions as drf_exceptions, viewsets
from .models import *
from .serializers import *
import logging

logger = logging.getLogger(__name__)

"""API Call"""


class BookViewSet(viewsets.ModelViewSet):

    lookup_field = 'gutenberg_id'

    queryset = Book.objects.exclude(download_count__isnull=True)
    queryset = queryset.exclude(title__isnull=True)

    serializer_class = BookSerializer

    def get_queryset(self):
        logger.info("Entering into method")
        queryset = self.queryset

        queryset = queryset.order_by('-download_count')

        # Book Ids Filtering
        id_string = self.request.GET.get('ids')
        if id_string is not None:
            logger.debug("Filter criteria is provided is ids {0}".format(id_string))
            ids = id_string.split(',')
            try:
                ids = [int(id) for id in ids]
            except ValueError:
                pass
            else:
                queryset = queryset.filter(gutenberg_id__in=ids)
        # Language Filtering
        language_string = self.request.GET.get('languages')
        if language_string is not None:
            logger.debug("Filter criteria is provided is language {0}".format(language_string))
            language_codes = [code.lower() for code in language_string.split(',')]
            queryset = queryset.filter(languages__code__in=language_codes)

        # Mimetype Filtering
        mime_type = self.request.GET.get('mime_type')
        if mime_type is not None:
            logger.debug("Filter criteria is provided is mime_type {0}".format(mime_type))
            queryset = queryset.filter(format__mime_type__startswith=mime_type)

        # Topic filtering
        topic = self.request.GET.get('topic')
        if topic is not None:
            logger.debug("Filter criteria is provided is topic {0}".format(topic))
            queryset = queryset.filter(
                Q(bookshelves__name__icontains=topic) | Q(subjects__name__icontains=topic)
            )

        # Author filtering
        author = self.request.GET.get('author')
        if author is not None:
            logger.debug("Filter criteria is provided is author {0}".format(author))
            queryset = queryset.filter(authors__name__icontains=author)

        # Title filtering
        title = self.request.GET.get('title')
        if title is not None:
            logger.debug("Filter criteria is provided is title {0}".format(title))
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()
