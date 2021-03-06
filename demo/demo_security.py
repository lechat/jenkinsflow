# This file is for configuring security for the demo and test jobs
# See the basic.py demo for how to do this with your own flows

# Note:

# Securitytoken and username/password are two different ways of allowing api access to execute (build) a job.
# You will however need both authentication methods, since neither can be used for everything

# Securitytoken is SIGNIFICANTLY faster than username/password
# If securitytoken is set, it will be used for executing (building) the jobs
# Securitytoken MUST be used in order for the flow job to ammend the 'build cause' of jobs that it invokes, if username/password
# is used the cause will always be 'Invoked by <username>'

# Username and password are needed for creating jobs and for changing build status with the 'Propagation.FAILURE_TO_UNSTABLE' feature
# The ./test/test.py script will need to create Jenkins jobs which REQUIRES username/password

securitytoken = 'jenkinsflow_securitytoken'

username = 'jenkinsflow_jobrunner'
password = '123123'
