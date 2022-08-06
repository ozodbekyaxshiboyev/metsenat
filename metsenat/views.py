import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.generics import CreateAPIView,DestroyAPIView
from rest_framework import mixins
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from .models import OTM, Sponsor, Student,StudentSponsor
from .serializers import OtmSerializer,SponsorSerializer, StudentSerializer,StudentSponsorSerializer,SponsorWatchserializer
from .serializers import UserSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions


class StaffPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff



class RegisterView(APIView):
    def post(self,request):
        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return  Response(serializer.data)


class OtmViewSet(ModelViewSet):
    serializer_class = OtmSerializer

    pagination_class = LimitOffsetPagination
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return OTM.objects.all()



class StudentListCreateApiView(ListCreateAPIView):   #todo OKEY
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentSerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['type_student', 'otm']
    search_fields = ["full_name"]

    def get_queryset(self):
        return Student.objects.all()


class StudentDetailDestroyApiView(RetrieveUpdateDestroyAPIView):  #todo OKEY
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentSerializer
    # lookup_field = 'pk'

    def get_queryset(self):
        return Student.objects.all()

    def get_object(self):
        student_pk = self.request.data.get('student_pk')
        if student_pk is not None:
            try:
                return Student.objects.get(pk=student_pk)
            except Student.DoesNotExist:
                raise ValidationError("student_pk xato")
        raise ValidationError("student_pk berilmadi")

    def get(self, request, *args, **kwargs):
        student = self.get_object()
        student_serializer = StudentSerializer(student)
        student1 = student_serializer.data

        #tasdiqlangan va homiyligik qilmagan sponsorlarning ismi va idsi junatilyapti
        items = student.sponsor.all().values_list('id', flat=True)
        queryset = Sponsor.objects.filter(status="Tasdiqlangan").exclude(id__in=items).values('id', 'full_name')
        sponsor_serializer = SponsorWatchserializer(queryset,many=True)
        sponsors = sponsor_serializer.data

        studentsponsor = student.studentsponsor_set.all()
        studentsponsor_serializer = StudentSponsorSerializer(studentsponsor, many=True, context=request)
        studentsponsor = studentsponsor_serializer.data

        my_data = {
            "student": student1,
            "sponsors": sponsors,
            "sponsorly": studentsponsor,
            "type_student": ["magistr", "bakalavr"]
        }

        return Response(my_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        student_all_get = student.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
        if student_all_get is None:
            student_all_get = 0
        if student_all_get > 0:
            raise ValidationError("Homiylik mablag`i ajratilgan talabani uchirib bo`lmaydi!")
        return super().delete(request,*args, **kwargs)



class StudentSupportApiView( DestroyAPIView, mixins.UpdateModelMixin, generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentSponsorSerializer
    # lookup_field = 'pk'

    def get_queryset(self):
        return StudentSponsor.objects.all()

    def get_object(self):
        support_pk = self.request.data.get('support_pk')
        if support_pk is not None:
            try:
                return StudentSponsor.objects.get(pk=support_pk)
            except StudentSponsor.DoesNotExist:
                raise ValidationError("support_pk xato")
        raise ValidationError("support_pk berilmadi")

    def put(self,request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self,request, *args, **kwargs):
        support = self.get_object()
        data = request.data
        serializer = StudentSponsorSerializer(instance = support, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SponsorAddApiView(CreateAPIView):  #todo OKEY
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentSponsorSerializer



class SponsorListCreateApiView(ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = SponsorSerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter,filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['status','amount_pay','created_date']
    search_fields = ["full_name"]


    def get_queryset(self):
        return Sponsor.objects.all()

    # def get_queryset(self):
    #     query = {}
    #     for item in self.request.GET.keys():
    #         query[item]=self.request.GET[item]
    #     print(query)
    #     return Sponsor.objects.filter(**query)   #todo filterga dict berish mumkin


class SponsorDetailApiView(RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, StaffPermission)
    serializer_class = SponsorSerializer
    # lookup_field = 'pk'

    def get_queryset(self):
        return Sponsor.objects.all()

    def get_object(self):
        sponsor_pk = self.request.data.get('sponsor_pk')
        if sponsor_pk is not None:
            try:
                return Sponsor.objects.get(pk=sponsor_pk)
            except Sponsor.DoesNotExist:
                raise ValidationError("sponsor_pk xato")
        raise ValidationError("sponsor_pk berilmadi")

    def delete(self, request, *args, **kwargs):
        sponsor = self.get_object()
        sponsor_all_give = sponsor.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
        if sponsor_all_give is None:
            sponsor_all_give = 0
        if sponsor_all_give > 0 or sponsor.status == "Tasdiqlangan":
            raise ValidationError("Homiylik mablag`i ajratilgan yoki Tasdiqlangan homiyni uchirib bo`lmaydi!")
        return super().delete(request,*args, **kwargs)



class DashboardApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,StaffPermission)

    def get(self, request):
        from datetime import date, timedelta, datetime
        end_date = date.today()
        start_date = end_date - timedelta(days=60)
        start = self.request.query_params.get("start")
        finish = self.request.query_params.get("finish")

        if start:
            try:
                start_date = date.fromisoformat(start)
            except ValueError:
                pass
            # start_date = datetime.strptime(start,'%y-%m-%d').date()
        if finish:
            try:
                end_date = date.fromisoformat(finish)
            except ValueError:
                pass

        print(start_date, end_date, 22)
        delta = end_date - start_date  # returns timedelta
        dashboard = dict()

        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            day = str(day)
            sponsor_count = Sponsor.objects.filter(created_date=day).count()
            student_count = Student.objects.filter(created_date=day).count()
            inner_dict = dict()
            inner_dict["sponsors"] = sponsor_count
            inner_dict["students"] = student_count
            dashboard[day] = inner_dict

        jami_tolangan = StudentSponsor.objects.all().aggregate(Sum('amount')).get('amount__sum')
        jami_soralgan = Student.objects.all().aggregate(Sum('amount_contract')).get('amount_contract__sum')

        my_data = {
            "dashboard":dashboard,
            "jami_tolangan":jami_tolangan,
            "jami_soralgan":jami_soralgan,
            "tolanishi_kerak":jami_soralgan - jami_tolangan
        }
        return Response(my_data, status=status.HTTP_200_OK)
