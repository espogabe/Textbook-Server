from types import *
from sqlwrapper import RESTWrapper


print 'Testing wrapper insert'
wr = RESTWrapper('localhost', 'textbooks', 'textbooks470', 'textbooks')
assert True == wr.insert('test', testing='valuepy12345', this='valuepy2')
print 'Test succeeded'

print 'Testing wrapper select'
wr = RESTWrapper('localhost', 'textbooks', 'textbooks470', 'textbooks')
l = wr.select_all('test', testing='valuepy12345')
assert type(l) is ListType, "l is not a list: %r" % l
print 'Test succeeded'

# TODO: curl server hits
# TODO: json conversion testing
# TODO: passthru testing
