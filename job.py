#!/usr/bin/env python

'''
    I wanted to do something with AngelList's API
'''

import json
import settings as s
import sys
# leverages Bugra's CLI - I needed to update it & wanted to easy include - will create test & PR soooon
import angel


#test_location_info = {1629: u'Cincinnati', 2029: u'Shanghai'}


JOB_TYPE = 'full-time'
QUALITY = 5


# Code to process JSON and create a AL's API object
#####dkd
###################

def parse_input():

     if not sys.stdin.isatty():
        global CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN
        try:
            cmd_input = json.load(sys.stdin)

            CLIENT_ID = cmd_input['CLIENT_ID']
            CLIENT_SECRET = cmd_input['CLIENT_SECRET']
            ACCESS_TOKEN = cmd_input['ACCESS_TOKEN']

        except:
            raise ValueError('Error processing JSON input - must be valid JSON')
     else:
         raise ValueError('You must provide a JSON structured input')


def pprint(input):
    print json.dumps(input)

def me(angel_h):

     global USER_INFO, SKILL_INFO, LEVEL_INFO

     USER_INFO = {}
     SKILL_INFO = {}
     LEVEL_INFO = {}
     # only want to call the API once
     me_result = angel_h.get_self()

     # grab location info
     for loc in me_result['locations']:
     #for loc in angel_h.get_self()['locations']:
         USER_INFO[loc['id']] = loc['display_name']

     # grab skill info
     for skill in me_result['skills']:
         SKILL_INFO[skill['id']] = skill['name']
         #SKILL_INFO[skill['id']]['level'] = '3' #skill['level']
     # TODO: build levels as nested dic/JSON

     # grab levels
     for level in me_result['skills']:
         LEVEL_INFO[level['id']] = level['level']

     return USER_INFO, SKILL_INFO, LEVEL_INFO

def pagination(method,id):

    results = []

    final_results = {}
    # TODO see note
    set_env =method(id)
    final_results = set_env
    last_page = set_env['last_page']
    current_page = 66    #needs to be set to to two
    job_results = {}

    while current_page < last_page: #page['last_page']:
        #job_results = request.get_tag_jobs(id, page = num)
        job_results = method(id,page=current_page)
        last_page = job_results['last_page']

        output = final_results['jobs'] + job_results['jobs']
        final_results['jobs'] = output


        current_page = current_page + 1

    return final_results


def get_all_jobs(angel_h,locations):
    jobs = []
    for location_id in locations:
        #print "%s location_id" % location_id
        temp_jobs = job_search_by_location(angel_h,location_id,JOB_TYPE)
        jobs = jobs + temp_jobs

    return jobs


def job_search_by_location(angel_h,location_id,job_type):
    jobs_result = {}   #might need to remove ?
    output =[]
    job_list = []
    api = angel_h.get_tag_jobs
    jobs = pagination(api,location_id)
    #print json.dumps(jobs)

    #sys.exit(555)
    #jobs = angel_h.get_tag_jobs(location_id)
    for job in jobs['jobs']:
        #print job['startup']['name']
        #if job['job_type'] == job_type and job[]
        for tag in job['tags']:
            #print tag['display_name']
            for skill_key in SKILL_INFO.keys():
                #print skill_key
                if tag['id'] == skill_key and job['job_type']== job_type and job['id'] not in jobs_result.keys() \
                        and job['startup']['quality'] > QUALITY:  # remove quality
                   # print tag['display_name']
                    temp_job = {'title': job['title'],
                                'job': job['angellist_url'],
                                'job_id':job['id'],
                                'startup':job['startup']['name'],
                                'quality':job['startup']['quality'],
                                'salary_min':job['salary_min'],
                                'salary_max':job['salary_max'],
                                'equity_min':job['equity_min'],
                                'equity_max':job['equity_max'],
                                'startup_id':job['startup']['id'],
                                'equity_vest':job['equity_vest'],
                                'equity_cliff':job['equity_cliff'],
                                'currency_code':job['currency_code']}

                    #print "temp job type %s" % type(temp_job)
                    #print temp_job
                    #sys.exit(33)
                    #temp_job.extend([job['title'],job['angellist_url']])
                    #jobs_result[job['id']] = temp_job

                    output.append(temp_job)
                    #jobs_result['jobs_by_location'] = output

                    #jobs_result['job_id'] = temp_job
    jobs_result['jobs_by_location'] = output   # REMOVE THIS?
                    #print temp_job
                    #if not tag['display_name'] in job_list: job_list.append(job)
                    #print json.dumps(job_list)
                    #sys.exit(333)
            #sys.exit(333)
    #print json.dumps(jobs_result)
    return output  # rename output?
    #return len(jobs_result['jobs_by_location'])

def stats(jobs):
    output = []
    stats_output =[]
    count = 0
    quality_total = 0
    startup_max = 0
    equity_cliff =0
    equity_vest = 0
    equity_max = 0

    for job in jobs:

        try:
            quality_total += int(job['quality'])
            startup_max += int(job['salary_max'])
            equity_max += float(job['equity_min'])
            equity_vest += float(job['equity_vest'])
            equity_cliff += float(job['equity_cliff'])
            count += 1
            output.append(job)
        except:
            # print "This are jobs that didn't have 100% data quality thus were not counted"
            #print json.dumps(job)
            pass

    # avgs
    quality_total /= count
    startup_max /= count
    equity_max  /= count
    equity_cliff /= count


    '''  print '%f quality_total' % quality_total
    print '%f startup_max' % startup_max
    print '%f equity_max' % equity_max
    print '%f equity_cliff' % equity_cliff
    print '%f equity_vest' % equity_vest
    print '%f count' % count'''
    stats_output = {'quality_total':quality_total, 'startup_max':startup_max, 'equity_max':equity_max, 'equity_cliff':equity_cliff, 'total_count':count}
    print stats_output['quality_total']

    #return {'output':output}, {'stats':{'quality_total':quality_total, 'startup_max':startup_max, 'equity_max':equity_max, 'equity_cliff':equity_cliff, 'total_count':count}}
    return {'output':output}, {'stats_output':stats_output}
    #sys.exit(3)
    #return {'output':output, 'stats_output':stats_output}


def path_startup(api_object,jobs_input):
    #print type(jobs)
    #print type(args)
    #print jobs
    #print args
    #print path_input['stats_output']['total_count']
    #sys.exit(77)
    count = 1
    path_avg = 0.0
    for job in jobs_input['output']:
        path = api_object.get_paths(startup_ids=job['startup_id'],direction='followed')
        #path = api_object.get_paths(startup_ids=144696,direction='followed')
        #print type(path)
        #print path.keys()
        #pprint(path.values())
        #print type(path['144696'])
        #print path
        #break


        if path:
            #pprint(path[str(job['startup_id'])])
            #pprint(len(path[str(job['startup_id'])]))
            #sys.exit(3)
            for connect in path[str(job['startup_id'])]:
                pprint(connect)
                count += 1
                path_avg += float(job['path'])
                job['path'] = len(connect)

                #pprint(len(connect))
                #pprint(job)
                pprint("-----------------")
        else:
            #print job
            #print job['startup_id']

            #print jobs_input['output'][str(job(['startup_id']))]
           # startup_id = str(job(['startup_id']))
            pprint(jobs_input['output'])
            sys.exit(3)
            print jobs_input['output'][34598]


        sys.exit(4)
        '''
                job['path'] = len(connect)
                pprint(job)
                path_avg += float(job['path'])
                count += 1
                pprint(count)
                pprint("-----------------")
                #sys.exit(4)
        path_avg /= count

        pprint(path_avg)
        '''
        '''
            #pprint(path)
            pprint(path[str(job['startup_id'][0])])
            pprint(len(path[str(job['startup_id'][0])]))
            sys.exit(33)
            #pprint(job)
            #print type(job)
            job['path'] = len(path)
            pprint(job)
            count += 1
            pprint(count)
            pprint("-----------------")
            sys.exit(33)




           for jaren in path['144696'][0]:
                #print type(jaren)
                print len(jaren)
                #pprint(jaren)
                sys.exit(33)
            sys.exit(33)
        print type(json.load(path['144696']))
        sys.exit(44)
        #print job['startup_id']
        if path:
            #print path.keys()
            #print job['startup_id']
            #print path['144696']
            #print path[str(job['startup_id'])]
            #print path[job['startup_id']]
            #pprint(path[str(job['startup_id'])])
            #print type(path[str(job['startup_id'])])
            #print [path[str(job['startup_id'])]].keys()
            path_json = path[str(job['startup_id'])]

            #path_json = json.loads(path[str(job['startup_id'])])
            print type(path_json)
            sys.exit(44)
            pprint(path_json)
            pprint(path_json.keys())
            pprint(path_json.values())
            sys.exit(44)
            for connector in path[str(job['startup_id'])]:
                #pprint(connector.)
                sys.exit(44)
            results = path.values()
            print "results are %s" % results
            print type(results)
            sys.exit(33)
            print type(path)
            for connection in path:
                print connection

            #pprint(api_object.get_paths(startup_ids=job['startup_id'],direction='followed'))
            #print type(api_object.get_paths(startup_ids=job['startup_id'],direction='followed'))
            sys.exit(4)
    #for job in path_input['output']:
        #print job

        #print api_object.get_paths(startup_ids=jobs['startup_id'],direction='followed')['connector']
        #sys.exit(77)
'''
def algorithm(jobs,*args):

    # unpack stats
    for arg in args:
        quality_total = arg['stats']['quality_total']
        startup_max = arg['stats']['startup_max']
        equity_max = arg['stats']['equity_max']
        equity_cliff = arg['stats']['equity_cliff']

    #print startup_max
    #sys.exit(444)

    for job in jobs['output']:
        print job.values()
        sys.exit(33)
    #for j in jobs:
        #print
        #print a['stats']['startup_max']
        #sys.exit(44)
    for job in jobs:
        print job
    sys.exit(33)

#input_4_algorithm = stats(job_search_by_location(al,1692,"full-time"))

#print algorithm(*input_4_algorithm)



def main ():
    parse_input()

    ANGEL_API_OBJECT = angel.AngelList(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)
    #sys.exit(44)
    LOCATION_INFO, SKILL_INFO, LEVEL_INFO = me(ANGEL_API_OBJECT)
    jobs_output_final = get_all_jobs(ANGEL_API_OBJECT,LOCATION_INFO)

    jobs_final,stats_output = stats(jobs_output_final)
    path_startup(ANGEL_API_OBJECT,jobs_final)
    #pprint(stats_output)
    #print type(stats_output['output'])
    #pprint(path_startup(ANGEL_API_OBJECT,stats_output))
    #pprint(path_startup(ANGEL_API_OBJECT,*stats_output))


if __name__ == "__main__":
    main()
    #print "we made it"

#print pagination(al.get_tag_jobs,1692)
