useraccounts = [
    ['Mat',  '3578'],
    ['James', '7980'],
    ['Steven',   '3850'],
    ['Carol',   '3698']
]

name = raw_input('User name: ')
password = raw_input('password code: ')

if [name, password] in useraccounts: print 'Access granted to the server'
