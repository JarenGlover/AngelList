#!/usr/bin/env python

'''
    I wanted to do something with AngelList's API
'''

import json
import sys
from time import gmtime, strftime

# leverages Bugra's CLI - I needed to update it & wanted to easy include - will create test & PR soooon
import angel


# setting to filter on the type of job to search for
JOB_TYPE = 'full-time'
# setting for getting all jobs with quality label of this and higher
QUALITY = 7
# defind the JSON w/ the jobs output after the process "top X" jobs
JOB_LIMIT = 10
# this will defind the file with all the jobs not only
'''try:
    OUTPUT_HANDLE = open("output.json", "w")
except IOError:
    print "Error trying to create a File Handle to file output.json"
'''

def pprint(input):
    ''' wraps output with a JSON dumps so I can use jq command to read the input - i love jq

    :param input: a string
    :return: that string as a JSON
    '''
    print json.dumps(input)


def parse_input():
    ''' Will validate then parse the JSON input - AngeList creds

    '''
    if not sys.stdin.isatty():
        # TODO make these non-globals and reutrn so can be unpacked
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

def me(angel_h):
    '''

    :param angel_h:
    :return: USER_INFO, SKILL_INFO, LEVEL_INFO which are dicts contains user, skill, and skill level info
    '''
    global USER_INFO, SKILL_INFO, LEVEL_INFO

    USER_INFO = {}
    SKILL_INFO = {}
    LEVEL_INFO = {}
    # only want to call the API once
    # calls the /me route to obtain information about self
    me_result = angel_h.get_self()

    # grab location info
    for loc in me_result['locations']:
        #for loc in angel_h.get_self()['locations']:
        USER_INFO[loc['id']] = loc['display_name']

    # grab skill info
    for skill in me_result['skills']:
        SKILL_INFO[skill['id']] = skill['name']
        #SKILL_INFO[skill['id']]['level'] = '3' #skill['level']

    # grab levels
    #TODO need to remove - didn't use
    for level in me_result['skills']:
        LEVEL_INFO[level['id']] = level['level']

    return USER_INFO, SKILL_INFO, LEVEL_INFO


def get_all_jobs(angel_h, locations):
    ''' Obtain all jobs that match the location_id provided

    :param angel_h: AngelList API Object
    :param locations: a dicts full of locations ids
    :return: an list of jobs with the same location id
    '''
    jobs = []
    for location_id in locations:

        #print "%s location_id" % location_id
        temp_jobs = job_search_by_location(angel_h, location_id, JOB_TYPE)
        # build the jobs into one job list to return to parse
        jobs = jobs + temp_jobs

    return jobs

def pagination(api_route, id):
    ''' A function to help deal with pagination functionally with Angel List

    :param api_route: the api route you want to call to parse multi pages
    :param id: parameters for the api_route
    :return: dict full of all results from all the pages
    '''

    final_results = {}

    # call once to see if we need to page
    set_env = api_route(id)
    final_results = set_env

    # identify the last page
    last_page = set_env['last_page']


    current_page = 0;
    job_results = {}
    output = []

    while current_page < last_page:  #page['last_page']:
        #job_results = request.get_tag_jobs(id, page = num)
        job_results = api_route(id, page=current_page)

        #TODO remove the below make sure didn't impact
        # last_page = job_results['last_page'] - the last page shouldn't change

        output = output + job_results['jobs']
        #output = final_results['jobs'] + job_results['jobs']
        #final_results['jobs'] = output

        current_page = current_page + 1
    final_results['jobs'] = output # check if this works
    return final_results

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


    for job in jobs['jobs']:

        for tag in job['tags']:

            for skill_key in SKILL_INFO.keys():

                #TODO look at jobs_results().keys? WHY - should it be based on output?
                #if tag['id'] == skill_key and job['job_type'] == job_type and job['id'] not in jobs_result.keys() \
                if tag['id'] == skill_key and job['job_type'] == job_type and job['startup']['quality'] > QUALITY:

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


                    output.append(temp_job)
                    #jobs_result['jobs_by_location'] = output

                    #jobs_result['job_id'] = temp_job
    #jobs_result['jobs_by_location'] = output  # REMOVE THIS?
    #print temp_job
    #if not tag['display_name'] in job_list: job_list.append(job)
    return output  # rename output?



#TODO - i don't think this max function works

def check_max(max, input):
    ''' Simple function to obtain the max value given two values

    :param input: current max
    :param max:
    :return: max of the two values
    '''
    if input > max:
        max = input
    return max

def stats(jobs):
    ''' calculates some stats (avg and max) on the input of jobs

    :param jobs: dict of jobs
    :return: two dicts objects representing the job dict and stats dict
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

    # loop over all jobs
    for job in jobs:
        # some data is null - we can't process that
        try:
            #avg
            ''' Didn't need so remove to add speed?
            max_quality_total = check_max(max_quality_total, int(job['quality']))
            max_startup_max = check_max(max_startup_max, int(job['salary_max']))
            max_equity_cliff = check_max(max_equity_cliff, float(job['equity_cliff']))
            max_equity_max = check_max(max_equity_max, float(job['equity_max']))
            max_equity_vest = check_max(max_equity_vest, float(job['equity_vest']))
            '''

            #max

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

    # calculate the avgs
    ''' Didn't need so remove to add speed?
    quality_total /= count
    startup_max /= count
    equity_max /= count
    equity_cliff /= count
    '''

    #build the stats dict

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

    :param api_object: Angel List API Ojbect
    :param jobs_input: job dict of all jobs
    :param stats_input: stats dict full of stats about said jobs
    :return: NONE
    '''
    OUTPUT_HANDLE = open("output.json", "w")
    final_output = []
    #rebuilt = {}
    top_ten = {}
    count = 0
    path_avg = 0.0
    for job in jobs_input['output']:
        # TODO send this path request with mitiple IDs for lest API calls :p
        path = api_object.get_paths(startup_ids=job['startup_id'], direction='followed')


        if path:


            '''try:
                OUTPUT_HANDLE.write(json.dumps(job,indent=4,sort_keys=True))
            except IOError:
                print "Error trying to write a job to the output.json file"
            '''
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

            else:
                pivot = min(top_ten,key=top_ten.get)
                if job['algorithm'] > top_ten[pivot]:
                    top_ten.pop(pivot,None)
                    top_ten[job['startup_id']] = job



    pprint("-----------------FINAL INFO---TOP TEN BELOW-----------------")
    pprint(top_ten)

    pprint("The total jobs that was eligible via a Path connection is below")
    pprint(count)
   # OUTPUT_HANDLE.close()


def main():
    ''' Main Function
    '''
    parse_input()

    ANGEL_API_OBJECT = angel.AngelList(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)
    pprint("time after API object %s" % (strftime("%Y-%m-%d %H:%M:%S", gmtime())))


    LOCATION_INFO, SKILL_INFO, LEVEL_INFO = me(ANGEL_API_OBJECT)
    pprint("time after me info found %s" % (strftime("%Y-%m-%d %H:%M:%S", gmtime())))

    jobs_output_final = get_all_jobs(ANGEL_API_OBJECT, LOCATION_INFO)
    pprint("time after all jobs are found from Angel list %s" % (strftime("%Y-%m-%d %H:%M:%S", gmtime())))

    jobs_final, stats_output = stats(jobs_output_final)
    pprint("time stats were calculated %s" % (strftime("%Y-%m-%d %H:%M:%S", gmtime())))

    path_startup(ANGEL_API_OBJECT, jobs_final, stats_output)
    pprint("time after path and algo value was calculated %s" % (strftime("%Y-%m-%d %H:%M:%S", gmtime())))



if __name__ == "__main__":
    main()
