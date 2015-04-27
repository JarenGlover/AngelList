#!/usr/bin/env python

'''
    I wanted to do something with AngelList's API
'''

import json
import sys

# leverages Bugra's CLI - I needed to update it & wanted to easy include - will create test & PR soooon
import angel


JOB_TYPE = 'full-time'
QUALITY = 5
JOB_LIMIT = 10


# Code to process JSON and create a AL's API object
#####dkd
###################

def parse_input():
    '''

    :return:
    '''
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
    '''

    :param input:
    :return:
    '''
    print json.dumps(input)


def me(angel_h):
    '''

    :param angel_h:
    :return:
    '''
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


def pagination(method, id):
    '''

    :param method:
    :param id:
    :return:
    '''

    final_results = {}

    set_env = method(id)
    final_results = set_env
    last_page = set_env['last_page']

    #TODO make sure this is zero

    current_page = 0;  #needs to be set to to two
    job_results = {}

    while current_page < last_page:  #page['last_page']:
        #job_results = request.get_tag_jobs(id, page = num)
        job_results = method(id, page=current_page)
        last_page = job_results['last_page']

        output = final_results['jobs'] + job_results['jobs']
        final_results['jobs'] = output

        current_page = current_page + 1

    return final_results


def get_all_jobs(angel_h, locations):
    '''

    :param angel_h:
    :param locations:
    :return:
    '''
    jobs = []
    for location_id in locations:
        #print "%s location_id" % location_id
        temp_jobs = job_search_by_location(angel_h, location_id, JOB_TYPE)
        jobs = jobs + temp_jobs

    return jobs


def job_search_by_location(angel_h, location_id, job_type):
    '''

    :param angel_h:
    :param location_id:
    :param job_type:
    :return:
    '''
    jobs_result = {}  #might need to remove ?
    output = []
    job_list = []
    api = angel_h.get_tag_jobs
    jobs = pagination(api, location_id)
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
                #TODO look at jobs_results().keys? WHY - should it be based on output?
                #if tag['id'] == skill_key and job['job_type'] == job_type and job['id'] not in jobs_result.keys() \
                if tag['id'] == skill_key and job['job_type'] == job_type and job['id'] \
                        and job['startup']['quality'] > QUALITY:  # remove quality
                    # print tag['display_name']
                    temp_job = {'title': job['title'],
                                'job': job['angellist_url'],
                                'job_id': job['id'],
                                'startup': job['startup']['name'],
                                'quality': job['startup']['quality'],
                                'salary_min': job['salary_min'],
                                'salary_max': job['salary_max'],
                                'equity_min': job['equity_min'],
                                'equity_max': job['equity_max'],
                                'startup_id': job['startup']['id'],
                                'equity_vest': job['equity_vest'],
                                'equity_cliff': job['equity_cliff'],
                                'currency_code': job['currency_code']}

                    #print "temp job type %s" % type(temp_job)
                    #print temp_job
                    #sys.exit(33)
                    #temp_job.extend([job['title'],job['angellist_url']])
                    #jobs_result[job['id']] = temp_job

                    output.append(temp_job)
                    #jobs_result['jobs_by_location'] = output

                    #jobs_result['job_id'] = temp_job
    #jobs_result['jobs_by_location'] = output  # REMOVE THIS?
    #print temp_job
    #if not tag['display_name'] in job_list: job_list.append(job)
    #print json.dumps(job_list)
    #print json.dumps(jobs_result)
    return output  # rename output?
    #return len(jobs_result['jobs_by_location'])


def check_max(input, max):
    '''

    :param input:
    :param max:
    :return:
    '''
    if input > max:
        max = input
    return max


def stats(jobs):
    '''

    :param jobs:
    :return:
    '''
    output = []
    stats_output = []
    count = 0
    quality_total = 0
    startup_max = 0
    equity_cliff = 0
    equity_vest = 0
    equity_max = 0
    max_quality_total = 0
    max_startup_max = 0
    max_equity_cliff = 0
    max_equity_vest = 0
    max_equity_max = 0
    for job in jobs:

        try:

            max_quality_total = check_max(max_quality_total, int(job['quality']))
            max_startup_max = check_max(max_startup_max, int(job['salary_max']))
            max_equity_cliff = check_max(max_equity_cliff, float(job['equity_cliff']))
            max_equity_max = check_max(max_equity_max, float(job['equity_max']))
            max_equity_vest = check_max(max_equity_vest, float(job['equity_vest']))
            #
            quality_total += int(job['quality'])
            startup_max += int(job['salary_max'])
            equity_max += float(job['equity_max'])
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
    equity_max /= count
    equity_cliff /= count

    stats_output = {'avg_quality_total': quality_total, 'avg_startup_max': startup_max, 'avg_equity_max': equity_max, \
                    'avg_equity_cliff': equity_cliff, 'total_count': count, 'max_quality_total': max_quality_total, \
                    'max_startup_max': max_startup_max, 'max_equity_cliff': max_equity_cliff, 'max_equity_max': \
        max_equity_max, 'max_equity_vest': max_equity_vest
    }
    #print stats_output['quality_total']

    #TODO review this print statment

    pprint(count)
    pprint("+++The total job counts is above++++")

    return {'output': output}, {'stats_output': stats_output}


def path_startup(api_object, jobs_input, stats_input):
    '''

    :param api_object:
    :param jobs_input:
    :param stats_input:
    :return:
    '''
    output_handle = open("output.json", "w")
    final_output = []
    #rebuilt = {}
    top_ten = {}
    count = 0
    path_avg = 0.0
    for job in jobs_input['output']:
        path = api_object.get_paths(startup_ids=job['startup_id'], direction='followed')


        if path:
            #print_help = json.loads(job)

            output_handle.write(json.dumps(job,indent=4,sort_keys=True))

            count += 1
            for connect in path[str(job['startup_id'])]:

                path_avg += float(len(connect))
                job['path'] = len(connect)

                job['algorithm'] = (stats_input["stats_output"]["max_equity_vest"] - float(job['equity_vest'])) + (
                    stats_input["stats_output"]["max_equity_cliff"] - float(job['equity_cliff'])) + float(job['path']) \
                                   + float(job['salary_min']) + float(job['quality']) + float(job['equity_min'])

            #rebuilt[job['startup_id']] = job
            final_output.append(job)


            if len(top_ten) < JOB_LIMIT:

                top_ten[job['job_id']] = job
                #pprint( print "This is ... %d and lenthis is %d" % (job['startup_id'], len(top_ten))
                # pprint(top_ten)
                #pprint("+++++")
            else:
                pivot = min(top_ten,key=top_ten.get)
                if job['algorithm'] > top_ten[pivot] and len(top_ten) <= 3:
                    top_ten.pop(pivot,None)
                    top_ten[job['startup_id']] = job



    pprint("-----------------")
    pprint(top_ten)
    pprint("The total jobs that was eligible via a Path connection is below")
    pprint(count)
    output_handle.close()


def main():
    '''

    :return:
    '''
    parse_input()

    ANGEL_API_OBJECT = angel.AngelList(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)
    #sys.exit(44)
    LOCATION_INFO, SKILL_INFO, LEVEL_INFO = me(ANGEL_API_OBJECT)
    jobs_output_final = get_all_jobs(ANGEL_API_OBJECT, LOCATION_INFO)

    jobs_final, stats_output = stats(jobs_output_final)

    #pprint(stats_output)
    #sys.exit(3)
    path_startup(ANGEL_API_OBJECT, jobs_final, stats_output)


if __name__ == "__main__":
    main()
    #print "we made it"

#print pagination(al.get_tag_jobs,1692)
