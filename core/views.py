from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from core.models import Person
from core.serializers import PersonSerializer
from rest_framework import status

# Create your views here.
@api_view()
def view_dtl(request):
    return Response({'success': 409, 'message': 'api'})



@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def view_person(request):
    # GET method to retrieve all persons
    if request.method == 'GET':
        person_obj = Person.objects.all()
        serializer = PersonSerializer(person_obj, many=True)
        return Response({'msg': 'Successfully retrieved data', 'data': serializer.data}, status=status.HTTP_200_OK)

    # POST method to create a new person
    elif request.method == 'POST':
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Person created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT method to update a person (full update)
    elif request.method == 'PUT':
        person_obj = Person.objects.get(pk=request.data.get('id'))
        serializer = PersonSerializer(person_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Person updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH method to partially update a person
    elif request.method == 'PATCH':
        person_obj = Person.objects.get(pk=request.data.get('id'))
        serializer = PersonSerializer(person_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Person updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE method to delete a person
    elif request.method == 'DELETE':
        person_obj = Person.objects.get(pk=request.data.get('id'))
        person_obj.delete()
        return Response({'msg': 'Person deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'msg': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)