import requests

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
import schools.models as schools_models


def query_api(api_endpoint_id):
    api_base  = 'http://gisweb2.ci.durham.nc.us/arcgis/rest/services/DurhamMaps/DPS_Schools/MapServer'
    api_get_params = {
            'outSR':'4326', #output spatial reference
            'where': '1=1', #grab all records
            'outFields' : '*', #all fields
            'f' : 'pjson'   #json file type
    }
    url = "%s/%s/query" % (api_base, api_endpoint_id)
    doc = requests.get(url, params=api_get_params)
    return doc.json()['features']


def query_api2(api_endpoint_id, api_section):
    api_base = 'http://gisweb2.ci.durham.nc.us/arcgis/rest/services/DurhamMaps/{api_section}/MapServer'.format(api_section=api_section)
    api_get_params = {
            'outSR':'4326', #output spatial reference
            'where': '1=1', #grab all records
            'outFields' : '*', #all fields
            'f' : 'pjson'   #json file type
    }
    url = "%s/%s/query" % (api_base, api_endpoint_id)
    doc = requests.get(url, params=api_get_params)
    return doc.json()['features']


def to_multipolygon(rings):
    polys = []
    for ring in rings:
        polys.append(Polygon(ring))
    return MultiPolygon(polys)


class Command(BaseCommand):
    help = 'Load up the data from GeoJSON into the models'

    SCHOOL_NORMALIZED_NAMES = {
        'Club Blvd': 'Club Boulevard',
        'Lakewood': 'Lakewood Elementary School',
        'Southern': 'Southern School of Energy and Sustainability',
        'Y.E. Smith': 'Y.E. Smith Elementary Museum School',
        'Performance Learning Center': 'Durham Performance Learning Center',
        'W.G. Pearson School - Student Services Center': 'W. G. Pearson Magnet Middle School ',
    }

    def get_school(self, name, schools):
        name_normalized = self.SCHOOL_NORMALIZED_NAMES.get(name, name)
        if name_normalized in schools:
            return schools[name_normalized]
        else:
            defaults = {
                'location': Point(0,0),
                'grade_max': -100,
                'grade_min': -100,
            }
            school, created = schools_models.School.objects.get_or_create(name=name_normalized, defaults=defaults)
            return school

    def load_school_points(self, schools={}):
        school_point_id = 0
        for school in query_api(school_point_id):
            name = school['attributes']['School'].strip()
            s = self.get_school(name, schools)
            s.location = Point(
                    float(school['geometry']['x']),
                    float(school['geometry']['y'])
            )
            s.address = school['attributes']['ADDRESS'].strip()
            if school['attributes']['MAGNET'] == 'Magnet':
                s.type = 'magnet'
            if school['attributes']['YEARROUND'] == "Year-Round":
                s.year_round = True
            s.level = school['attributes']['TYPE_'].lower()
            s.website_url = school['attributes']['WEBSITE']
            s.grade_min = school['attributes']['Low_Grade']
            s.grade_max = school['attributes']['Top_Grade']
            schools[name] = s
        return schools


    def load_districts(self, schools={}):
        for api_id in (1, 2, 3):
            for district_json in query_api(api_id):
                name = district_json['attributes']['DISTRICT'].strip()
                s = self.get_school(name, schools)
                s.district = to_multipolygon(district_json['geometry']['rings'])
                s.type = 'neighborhood'
                schools[name] = s
        return schools

    def load_zones(self, schools={}):
        school_walkzone_id = 6
        for school in query_api(school_walkzone_id):
            name = school['attributes']['NAME'].strip()
            s = self.get_school(name, schools)
            s.type = 'magnet'
            zone = to_multipolygon(school['geometry']['rings'])
            zone_type = school['attributes']['TYPE_']
            if zone_type == "Walk Zone":
                s.walk_zone = zone
            if zone_type == "Choice Zone":
                s.choice_zone = zone
            if zone_type == "Priority Zone":
                s.priority_zone = zone
            schools[name] = s
        return schools

    def load_year_round_elementary(self, schools={}):
        api_end_point = 3
        api_section = 'DPS_ElementaryStudentAssignment'
        for school in query_api2(api_end_point, api_section):
            name = school['attributes']['YEARRND_ES'].strip()
            s = self.get_school(name, schools)
            s.type = 'magnet'
            s.year_round_zone = to_multipolygon(school['geometry']['rings'])
            schools[name] = s
        return schools

    def load_year_round_middle(self, schools={}):
        api_end_point = 2
        api_section = 'DPS_MiddleSchoolStudentAssignment'
        for school in query_api2(api_end_point, api_section):
            name = school['attributes']['YEARRND_MS'].strip()
            s = self.get_school(name, schools)
            s.type = 'magnet'
            s.year_round_zone = to_multipolygon(school['geometry']['rings'])
            schools[name] = s
        return schools

    def load_sandy_ridge_priority_zone(self, schools={}):
        # special case for Sandy Ridge Priority Zone.  See issue #99
        api_end_point = 6
        api_section = 'DPS_ElementaryStudentAssignment'
        for school in query_api2(api_end_point, api_section):
            if school['attributes']['SR_TRANSPO'] == 'Sandy Ridge Transportation Services Area':
                name = 'Sandy Ridge'
                s = self.get_school(name, schools)
                s.priority_zone = to_multipolygon(school['geometry']['rings'])
                schools[name] = s
        return schools

    def load_traditional_option_zones(self, schools={}):
        api_endpoint_id = 7
        api_section = 'Holt_Easley_Traditional_Options'
        for school in query_api(api_endpoint_id):
            name = school['attributes']['TRAD_OPT'].strip()
            s = self.get_school(name, schools)
            s.traditional_option_zone = to_multipolygon(school['geometry']['rings'])
            schools[name] = s
        return schools

    def handle(self, *args, **options):
        schools = {}
        schools = self.load_school_points(schools)
        schools = self.load_districts(schools)
        schools = self.load_zones(schools)
        schools = self.load_year_round_elementary(schools)
        schools = self.load_year_round_middle(schools)
        schools = self.load_sandy_ridge_priority_zone(schools)
        schools = self.load_traditional_option_zones(schools)
        for name in schools.keys():
            schools[name].save()
