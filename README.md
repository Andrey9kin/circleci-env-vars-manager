# create/update/delete env variables in all CircleCI projects that you follow

A small tool to manage a huge headache. Think you exposed a secret that is provided as an environment variable and now need to change it in all projects... This is how you do it
```
# a little bit of preparations - install all deps as virualenv and activate it
bash -e setup.sh
source env/bin/activate
```
```
# will only update projects that have SCREWED_VAR variable
python3 circleci-manage-env-vars.py --token 5842f69d00e237f7acirclecitoken838c25b3cd2cef --action update --name SCREWED_VAR --value SOME_NEW_VALUE
```
Or say you need to create a variable in all projects
```
# will override VAR_NAME if exists
python3 circleci-manage-env-vars.py --token 5842f69d00e237f7acirclecitoken838c25b3cd2cef --action create --name VAR_NAME --value SOME_VALUE 
```
Or delete env variable from all projects
```
python3 circleci-manage-env-vars.py --token 5842f69d00e237f7acirclecitoken838c25b3cd2cef --action delete --name VAR_NAME  
```
You are welcome!

## Note!
Will only update projects that user with the provided token is following. This is how CircleCI API works - if you know another way of getting all projects for org then please reach out to create an issue
Also, docopt, that is used for parsing args, is sensetive to the order of arguments so please specify arguments in the order as shown above

## P.S.

Another way of working out this issue is to make use of CircleCI [contexts](https://circleci.com/docs/2.0/contexts/)
