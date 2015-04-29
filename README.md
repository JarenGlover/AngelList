# AngelList
a simple hack with AngelList's API

###What?
An Python based application, that when given some AngelList related information it will leverage your AngelList related information to generate "top ten" jobs realted to yoru AngelList profile. This will levearege the AngelList API. I was pretty impress overall at the quality and quality of the API. 

### Inputs
The program requires three inputs client id, client secret, and access token. These three variables must be provided for the programs to leverage your information on AngelList. You can obtain these items by creating an [AngelList application](https://angel.co/api/oauth/clients/new). [This is because they require [OAuth](https://angel.co/api/oauth/faq) for some API calls]. An example file can be found under the name "input.json". 

{
     
      "CLIENT_ID": "",
        
      "CLIENT_SECRET": "",
            
       "ACCESS_TOKEN": ""
}

You can the program from the command with the below command combination.`python job.py < input.json`

I usually run it like below:

`$ time python job.py < input.json.old | jq '.' > top_ten.json.new
`

`real 13m3.826s user    0m9.367s sys 0m1.273s`

My account processed 1000+ plus jobs so it takes a little time. Sorry with restructed later....use [numpy](http://www.numpy.org/) or something ...

Basic Flow of the application:
1. Parse the input file to verify it is an legit JSON struture 
2. Create an API object using the information from Step 1. 
3. Collection Location and Skill information from your account using [me/ route](https://angel.co/api/spec/users#GET_me).
4. Use the location ids found in your account to search for jobs that match your skill (skill ids) tag information. This information is provided by the [tags jobs route](https://angel.co/api/spec/jobs#GET_tags_%3Atag_id_jobs).
5. Processed all those jobs (could be 1k+) to see 
6. Generate somes stats based on all the jobs returned to help rank the jobs.
7. For each job idenitfy a path value to see how related or unrelated you are to this job. (ie. is someone in your angellist network who connect you with this startup). This uses the [/path route](https://angel.co/api/spec/paths#GET_paths). I know this should have been done in the same loop in step 6. 

Please note that the some method (path_startup) that caculates the path also generate a value for each job. The value is simple a addition of the 

1. Job's Equity Vest #
2. Job's Equity Cliff #
3. Job's Path Value (only returns jobs that have a path value)
4. Job's Salary Min #
5. Job's Equity Min #

There is some assumption built into the program. 
- Your Angel List profile is robust - i.e. location, skills, network etc
- You are looking for full time jobs (this can be change in the static varible)
- You only want employeers of jobs who [quality](https://angel.co/api/spec/startups#GET_startups_%3Aid) is at least 6.
- Writes the top list of jobs that qualify based on the above assumption to a file called "output.json". This too can be changed

######FYI: I used the  quickest Python based API I could find. It was a bit updated so I incorp those changes and pulled directly into my project to help with the onboarding process. I plan to update the CLI and do a pull request. So one could do a simple pip install. 

