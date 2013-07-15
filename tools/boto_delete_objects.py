#!/usr/bin/env python

import os
import sys
import boto

if(len(sys.argv) != 2):
    sys.stderr.write('USAGE: %(p)s <bucket>\n' % {'p':sys.argv[0]})
    sys.exit(-1)

bucket_name=sys.argv[1]

# Delete objects from bucket
conn=boto.connect_s3()
bucket=conn.get_bucket(bucket_name)
for key in bucket.list():
    bucket.delete_key(key)
    print 'Deleted object', key

# Exit
sys.exit(0)



