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
     # TODO: build levels as nested dic/JSON

     # grab levels
     for level in me_result['skills']:
         level_info[level['id']] = level['level']

     return user_info, skill_info, level_info

#pprint(me(al))

user_info, skill_info, level_info = me(al)
#print skill_info.keys()
#sys.exit(33)

def pagination(method,id):

    results = []

    final_results = {}
    current_page = 1
    job_results = {}
    set_env =method(id)
    #print job_results['last_page']
    # sys.exit(44)
    #last = job_results['last_page']
    last_page = set_env['last_page']
    #last_page = 1000000000
    #while job_results['page'] != 2: #page['last_page']:
    while current_page <= last_page: #page['last_page']:
        #job_results = request.get_tag_jobs(id, page = num)
        job_results = method(id,page=current_page)
        last_page = job_results['last_page']
        '''for res in job_results['jobs']:
            print json.dumps(res['title'])
            results.append(res)
            #final_results[current_page] = res
            break
        '''
        return job_results

        break
        current_page = current_page + 1
        #print "------------------------------"
        #print results['jobs']['title']
        #print results['page']
    #print len(results)
    #final_results['jobs'] = results
    #return json.dumps(final_results)
    return json.dumps(results)


def job_search_by_location(angel_h,location_id,job_type):
    jobs_result = {}
    job_list = []
    api = angel_h.get_tag_jobs
    jobs = pagination(api,location_id)
    #print jobs
    #sys.exit(555)
    #jobs = angel_h.get_tag_jobs(location_id)
    for job in jobs['jobs']:
        #print job['startup']['name']
        #if job['job_type'] == job_type and job[]
        for tag in job['tags']:
            #print tag['display_name']
            for skill_key in skill_info.keys():
                #print skill_key
                if tag['id'] == skill_key and job['job_type']== job_type and job['id'] not in jobs_result.keys():
                   # print tag['display_name']
                    temp_job = {'title': job['title'],
                                'job': job['angellist_url'],
                                'startup':job['startup']['name'],
                                'quality':job['startup']['quality'],
                                'startup_min':job['salary_min'],
                                'startup_max':job['salary_max']}

                    #temp_job.extend([job['title'],job['angellist_url']])
                    jobs_result[job['id']] = temp_job
                    #print temp_job
                    #if not tag['display_name'] in job_list: job_list.append(job)
                    #print json.dumps(job_list)
                    #sys.exit(333)
            #sys.exit(333)
    #print json.dumps(jobs_result)
    return jobs_result





pprint(job_search_by_location(al,1629,"full-time"))
sys.exit(33)




print pagination(al.get_tag_jobs,1692)

sys.exit(33)
#pprint(job_search_by_location(al,1629,"full-time"))

##page = al.get_tag_jobs(1692,page=3)
#print page['last_page']
#print page['page']

#pprint(me(al))




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