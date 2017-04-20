#!coding:utf-8
import xml.etree.cElementTree as ET 
from pymongo import MongoClient
client = MongoClient()
conn = client.paper_rank
collection = conn.papers

file = '../../../raw_data/paper_info.xml'
iterparser = ET.iterparse(file, events=('start', 'end'))
ns = {'xmlns':'http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord'}
REC = '{' + ns['xmlns'] + '}' + 'REC'
cnt = 0
for event, elem in iterparser:
	if event == 'end' and elem.tag == REC:
		UID = elem.find('xmlns:UID',ns).text
		titles_elem = elem.find('xmlns:static_data/xmlns:summary/xmlns:titles', ns)
		title_elem_s = titles_elem.findall('xmlns:title', ns)
		journal = ''
		name = ''
		for title_elem in title_elem_s:
			if title_elem.attrib['type'] == 'source':
				journal = title_elem.text
			if title_elem.attrib['type'] == 'item':
				name = title_elem.text
		if name != '' and journal != '':
			#在此发现了一个问题,就是数据库访问确实一个程序性能的瓶颈,在不需要update的时候,程序计数器cnt增长地很快,
			#当需要更新数据库的时候,cnt的增长减缓
			ret = collection.update_one({"_id":UID, "name":{"$exists":0}}, {"$set":{"name":name, "journal":journal}})
		if cnt%100 == 0:
			print cnt
		cnt += 1
		#下面这一句至关重要,不然就会内存泄露并最终耗尽内存
		elem.clear()