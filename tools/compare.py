import pandas as pd
import sys

pd.options.display.max_rows = 1000
pd.options.display.width = 1000

def qry(j, level):
    return j[j[level + ' cfd'] != j[level]][['address', level, level+' cfd']]

dps = pd.read_csv('dps.csv')
cfd = pd.read_csv('cfd.csv')

# filter out dps to found addresses
dps = dps[dps['lookup'] == 'OK']

# match DPS tool by showing assigned year round elementary as 
# year round option too.
def yr(row):
    if row['elementary school'] in ('Holt', 'Easley'):
        return row['elementary school']
    else:
        return row['year round elementary']

cfd['year round elementary'] = cfd.apply(yr, axis=1)

# join cfd and dps so we can compare
j = cfd.join(dps, how='inner', lsuffix=' cfd')

# normalize some names
j[j['elementary school cfd'] == 'Lakewood Elementary School'] = 'Lakewood'
j[j['elementary walk zone cfd'] == 'Club Boulevard'] = 'Club Blvd'
j[j['high school cfd'] == 'Southern School of Energy and Sustainability'] = 'Southern'
j = j.fillna('NULL') 

print('number of DPS addresses used in comparison ', len(j))
print('the following are the differences by school type.')

print('\n\nhigh school\n', qry(j, 'high school'))

print('\n\nmiddle school\n', qry(j, 'middle school'))
print('\n\nyear round middle school\n', qry(j, 'year round middle school'))

print('\n\nelementary school\n', qry(j, 'elementary school'))
print('\n\nyear round elementary\n', qry(j, 'year round elementary'))
print('\n\nelementary walk zone\n', qry(j, 'elementary walk zone'))
print('\n\nelementary choice zone\n', qry(j, 'elementary choice zone'))
print('\n\nelementary priority zone\n', qry(j, 'elementary priority zone'))

print('\n\nholt easley traditional option\n', qry(j, 'holt easley traditional option'))

