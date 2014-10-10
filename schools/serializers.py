from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers

import schools.models as schools_models

class SchoolSerializer(geo_serializers.GeoModelSerializer):
    eligibility = serializers.SerializerMethodField('get_eligibility')

    class Meta:
        model = schools_models.School
        #TODO Add back district?
        fields = ('id', 'name', 'level', 'address', 'type', 'eligibility', 'location')

    def get_eligibility(self, obj):
       import random
       #TODO
       #Assigned schools are blue
       #Option schools are orange
       #Others are gray
       return random.choice(('assigned', 'option'))
