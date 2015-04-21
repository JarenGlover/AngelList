#!/usr/bin/env python

'''
    I wanted to do something with AngelList's API
'''

import json
import settings as s
import sys
sys.path.append('/Users/Glove/Desktop/lob/angel-list/angel')
# the input should be creditals


import angel

al = angel.AngelList(s.CLIENT_ID, s.CLIENT_SECRET, s.ACCESS_TOKEN)
#print al

def pprint(input):
    print json.dumps(input)

def me(angel_h):
     user_info = {}
     skill_info = {}
     level_info = {}
     # only want to call the API once
     me_result = angel_h.get_self()

     # grab location info
     for loc in me_result['locations']:
     #for loc in angel_h.get_self()['locations']:
         user_info[loc['id']] = loc['display_name']

     # grab skill info
     for skill in me_result['skills']:
         skill_info[skill['id']] = skill['name']
         #skill_info[skill['id']]['level'] = '3' #skill['level']

     # grab levels
     for level in me_result['skills']:
         level_info[level['id']] = level['level']

     return user_info, skill_info, level_info
#me = me()



pprint(me(al))




def getSkills(angel,level=3):
    '''
    Return a dic of skills based on the skills tag for users
    :param angel:
    :return:
    '''
    skills = []
    for x in angel.get_self()['skills']:
        #print x['id']
        if x['level'] >= level:
            #print x['name']
            skills.append(x['id'])
  #  print skills
    return skills


# search for jobs based on the skills i'm best at

def jobs_by_id(angel,skills_ids):
    for skill in skills_ids:
        print skill
        companies = []
        for employer in angel.get_tag_jobs(skill)['jobs']:
            if employer['startup']['quality'] > 8:
                companies
           # print employer['name']['quality']
            sys.exit(187)

        '''    for startup in json.dumps(employer['startup']):
                print startup['name']
                print type(startup)
                sys.exit(888)

            sys.exit(187)
             if startup['quality'] > 7:
                    print employer['quality']
                    companies.append()'''




#pprint(getSkills(al,3))
#pprint(al.get_tag_jobs(98210))
#jobs_by_id(al,getSkills(al,3))



#angel.get_tag_jobs(id)
#print al.get_jobs(page=1)



#print al.get_search('bitcoin','Startup')
#print al.get_startup('page=1')
#print json.dumps(al.get_self()['skills'])

#print al.get_tags('1')
#print first_page_jobs