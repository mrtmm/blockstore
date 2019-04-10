'''
Views for Tags and Taxonomies.
'''
import logging

from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from tagstore.models import (
    Entity, EntityId,
    Tag,
)

from tagstore.tagstore_rest.serializers import EntitySerializer, EntityDetailSerializer, TagSerializer

logger = logging.getLogger(__name__)


class EntityViewSet(viewsets.ViewSet):
    '''
    ViewSet for Entity model and its tags.
    '''

    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

    def list(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        '''
        Get a list of all entities.
        '''
        serializer = EntitySerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, entity_type=None):  # pylint: disable=unused-argument
        '''
        Get a single entity. Never raises a 404, because Tagstore doesn't know
        which entities exist or not. If you want to know whether or not the
        entity is persisted in Tagstore's database, check the resulting
        "persisted" boolean field.
        '''
        try:
            entity = Entity.objects.get(external_id=pk, entity_type=entity_type)
        except Entity.DoesNotExist:
            entity = Entity(external_id=pk, entity_type=entity_type)
        serializer = EntityDetailSerializer(entity)
        return Response(serializer.data)

    def has_tag(self, request, pk, entity_type, taxonomy_id, tag_name):  # pylint: disable=unused-argument
        """
        Does this entity have the given tag?
        Use this if you need to check if an entity has one specific tag, as it
        will be faster than loading the entity's entire tag list.
        Raises 404 if the tag does not exist.
        """
        try:
            entity = Entity.objects.get(external_id=pk, entity_type=entity_type)
        except Entity.DoesNotExist:
            raise NotFound("Entity has no tags")
        try:
            tag = entity.tags.get(taxonomy_id=taxonomy_id, name=tag_name)
        except Tag.DoesNotExist:
            raise NotFound("Entity does not have that tag")
        return Response(TagSerializer(tag).data)

    def add_tag(self, request, pk, entity_type, taxonomy_id, tag_name):  # pylint: disable=unused-argument
        """
        Add the given tag to the entity.

        Only raises an error if the tag does not exist.
        TODO: Add an option to auto-create the tag.
        """
        try:
            tag = Tag.objects.get(taxonomy_id=taxonomy_id, name=tag_name)
        except Tag.DoesNotExist:
            raise NotFound("Tag does not exist")
        tag.add_to(EntityId(external_id=pk, entity_type=entity_type))
        return Response(TagSerializer(tag).data)

    def remove_tag(self, request, pk, entity_type, taxonomy_id, tag_name):  # pylint: disable=unused-argument
        """
        Remove the given tag from the entity.

        Only raises an error if the tag does not exist.
        TODO: Add an option to auto-delete the tag from the taxonomy if it's not
        applied to any other entities.
        """
        try:
            tag = Tag.objects.get(taxonomy_id=taxonomy_id, name=tag_name)
        except Tag.DoesNotExist:
            raise NotFound("Tag does not exist")
        tag.remove_from(EntityId(external_id=pk, entity_type=entity_type))
        return Response({})
