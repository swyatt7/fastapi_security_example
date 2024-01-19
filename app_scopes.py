'''
Following the JWT description on SciTokens (https://scitokens.org/technical_docs/Claims),
we will follow their notation on defining scopes:
    * read      : Read data from a resource
    * write     : Write data to a resource
    * queue     : Submit a task or a job to a queueing service
    * execute   : Immediately launch or execute a task

'''

API_SCOPE_DICT = {
    "/read_foo/" : [
        "read:/",
        "read:/foo"
    ]
}