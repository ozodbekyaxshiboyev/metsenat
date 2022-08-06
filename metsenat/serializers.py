from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from  .models import OTM,Sponsor,Student,StudentSponsor
from django.contrib.auth.models import User
from django.db.models import Sum


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {
            'password':{'write_only':True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class OtmSerializer(serializers.ModelSerializer):

    class Meta:
        model = OTM
        fields = '__all__'
        

class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = ('id','full_name','phone','amount_pay','is_company','status','company_name','created_date','pay_type',)
        extra_kwargs = {
            'created_date': {'read_only': True}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['ajratilgan'] = instance.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
        return representation

    def update(self, instance, validated_data):
        print("update ishladi")
        sponsor_all_give = instance.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
        if sponsor_all_give is None:
            sponsor_all_give = 0
        status = validated_data.get('status')
        if status is not None:
            if (instance.status == "Tasdiqlangan" or instance.status == "Moderatsiyada") and status == "Yangi":
                raise serializers.ValidationError("Statusni dastlabki holatga qaytarib bo`lmaydi!")
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.amount_pay = validated_data.get('amount_pay', instance.amount_pay)
        instance.is_company = validated_data.get('is_company', instance.is_company)
        instance.status = validated_data.get('status', instance.status)
        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.pay_type = validated_data.get('pay_type', instance.pay_type)
        if instance.is_company and instance.company_name is None:
            raise serializers.ValidationError("Korxona nomi kiritilmadi")
        if instance.is_company is False and instance.company_name:
            raise serializers.ValidationError("Bu homiy yuridik shaxs emas")
        if instance.amount_pay < sponsor_all_give:
            name = "Xatolik. Bu homiyning hisobidan yangi kiritilgan mablag`dan ko`proq mablag` homiylikka yo`naltirib bo`lingan!"
            raise serializers.ValidationError(name)
        if (instance.status == "Yangi" or  instance.status == "Moderatsiyada") and instance.pay_type:
            raise serializers.ValidationError("Moderatsiyadagi yoki Yangi homiy uchun to`lov turini tanlab bo`lmaydi!")
        if (instance.status == "Tasdiqlangan" or  instance.status == "Bekor qilingan") and instance.pay_type is None:
            raise serializers.ValidationError("To`lov turi tanlanmadi!")
        instance.save()
        return instance

    def create(self, validated_data):  #bu eng oxirgi ish validatsiyalardan keyingi, yangi create qilish uchun
        print("create ishladi")
        data = dict()
        data["full_name"] = validated_data.get('full_name')
        data["phone"] = validated_data.get('phone')
        data["amount_pay"] = validated_data.get('amount_pay')
        data["is_company"] = validated_data.get('is_company')
        company_name= validated_data.get('company_name')

        if company_name is not None:
            data["company_name"] = validated_data.get('company_name')
        is_company = data.get('is_company')

        if is_company and company_name is None:
            raise serializers.ValidationError("Korxona nomi kiritilmadi")
        if is_company is False and company_name:
            raise serializers.ValidationError("Bu homiy yuridik shaxs emas")
        return Sponsor.objects.create(**data)


class SponsorWatchserializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    full_name = serializers.CharField(required=True, max_length=200)


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"
        extra_kwargs = {
            'created_date': {'read_only': True}
        }

    def to_representation(self, instance):    #getda ishlasa kerak qo`shimcha fieldlar qo`shsa bo`ladi
        representation = super().to_representation(instance)
        student_all_get = instance.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
        if student_all_get is None:
            student_all_get = 0
        representation['olingan'] = student_all_get
        return representation

    def validate(self, attrs):
        print(3, attrs)
        return attrs

    def update(self, instance, validated_data):  #todo update qilinayotgnada ishlaydi put yoki patchda
        print("update ishladi")
        student_all_get = instance.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
        if student_all_get is None:
            student_all_get = 0

        instance.amount_contract = validated_data.get('amount_contract', instance.amount_contract)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.type_student = validated_data.get('type_student', instance.type_student)
        instance.otm = validated_data.get('otm', instance.otm)
        if instance.amount_contract < student_all_get:
            raise serializers.ValidationError("Xatolik! Bu talabaga ajratilgan mablag` yangi kiritilgan mablag`dan ko`p!")
        instance.save()
        return instance


class StudentSponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSponsor
        fields = ('id','student','sponsor','amount','created_date',)
        extra_kwargs = {
            'created_date': {'read_only': True}
        }

    def validate_amount(self,value):
        if value <= 0:
            raise ValidationError(detail='Kontrakt mablag`i xato kiritildi')
        return value

    def to_representation(self, instance):    #bu getda yuborish uchun faqat
        representation = super().to_representation(instance)
        representation['sponsor_full_name'] = instance.sponsor.full_name
        return representation

    def update(self, instance, validated_data):  #bu eng oxirgi ish validatsiyalardan keyingi, update qilish uchun
        print("update ishladi")
        if instance.student != validated_data.get('student'):
            raise serializers.ValidationError("Talaba idsi xato kiritildi")
        if instance.sponsor != validated_data.get('sponsor'):
            raise serializers.ValidationError("Homiy idsi xato kiritildi")
        changing_amount = instance.amount
        student_all_get =instance.student.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
        sponsor_all_give = instance.sponsor.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')

        new_amount = validated_data.get('amount')
        if new_amount is None:
            new_amount = 0
        result_amount = student_all_get - changing_amount + new_amount
        errorr: str = ""
        if result_amount > instance.student.amount_contract:
            errorr += "Bu pul miqdori talaba kontrak miqdoridan ko`p, "
        if instance.sponsor.amount_pay < sponsor_all_give - changing_amount + new_amount:
            errorr += "homiyning mablag`i bu o`tkazmaga yetmaydi!"
        if errorr != "":
            raise serializers.ValidationError(errorr)

        instance.student = validated_data.get('student', instance.student)
        instance.sponsor = validated_data.get('sponsor', instance.sponsor)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance

    def create(self, validated_data):  #bu eng oxirgi ish validatsiyalardan keyingi, yangi create qilish uchun
        data = validated_data
        student = data.get('student')
        sponsor = data.get('sponsor')
        new_amount = data.get('amount')
        if new_amount is None:
            new_amount = 0
        student_all_get = student.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
        sponsor_all_give = sponsor.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
        if student_all_get is None:
            student_all_get = 0
        if sponsor_all_give is None:
            sponsor_all_give = 0

        result_amount = student_all_get + new_amount
        print(34, result_amount)
        print(35, student.amount_contract)
        errorr: str = ""
        if result_amount > student.amount_contract:
            errorr += "Bu pul miqdori talaba kontrak miqdoridan ko`p, "
        if sponsor.status != 'Tasdiqlangan': \
                errorr += "homiy hali tasdiqlanmagan, "
        if sponsor.amount_pay < sponsor_all_give + new_amount:
            errorr += "homiyning mablag`i bu o`tkazmaga yetmaydi!"
        if errorr != "":
            raise serializers.ValidationError(detail=errorr)
        return StudentSponsor.objects.create(**validated_data)
