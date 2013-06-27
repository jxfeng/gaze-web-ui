#!/usr/bin/env python

import os
import sys
import boto
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import NUMBER

if(len(sys.argv) != 2):
    sys.stderr.write('USAGE: %(p)s <table-name>\n' % {'p':sys.argv[0]})
    sys.exit(-1)

table_name=sys.argv[1]

# Delete entries from table
table = Table(table_name)
items = table.scan()
for it in items:
    ret = it.delete()
    print 'Deleted', ret

# Exit
sys.exit(0)



