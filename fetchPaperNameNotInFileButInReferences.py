#!coding:utf-8
import xml.etree.cElementTree as ET 
from pymongo import MongoClient
client = MongoClient()
db = client.paper_rank
collection = db.papers

cursor = collection.find({"name": {"$exists": 0}})
print "Currently Do Not Have a Name: {}".format(cursor.count())

file = '../../../raw_data/paper_info.xml'
iterparser = ET.iterparse(file, events=('start', 'end'))
ns = {'xmlns':'http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord'}
REC = '{' + ns['xmlns'] + '}' + 'REC'
cnt = 0

for event, elem in iterparser:
	if event == 'end' and elem.tag == REC:
		references_elem = elem.find('xmlns:static_data/xmlns:fullrecord_metadata/xmlns:references', ns)
		reference_elem_s = references_elem.findall('xmlns:reference', ns)
		UID = ''
		journal = ''
		name = ''
		for reference_elem in reference_elem_s:
			try:
				UID = reference_elem.find('xmlns:uid', ns).text
				name = reference_elem.find('xmlns:citedTitle', ns).text
				journal = reference_elem.find('xmlns:citedWork', ns).text
			except Exception as e:
				print 'except:', e
				continue
			else:
				ret = collection.update_one({"_id": UID, "name": {"$exists": 0}}, {"$set": {"name": name, "journal": journal}})
		if cnt%100 == 0:
			print cnt
		cnt += 1
		#下面这一句至关重要,不然就会内存泄露并最终耗尽内存
		elem.clear()
