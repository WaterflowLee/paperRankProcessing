var client = new Mongo();
var db = client.getDB("paper_rank");
var collection_to = db.time_line;
var collection_from = db.papers;
var rets = [];
for (var interval=1;interval<=30;interval++) {
	var lv_field = "loss_value." + interval;
	var pipeline = [{"$match": {[lv_field]: {"$exists": 1}}},
					{"$group": {"_id": "$time", "avg_lv": {"$avg": "$"+ lv_field}}},
					{"$sort": {"_id":1}}];
	rets.push({
		_id:interval,
		time_line:collection_from.aggregate(pipeline).toArray()
	});
}
collection_to.insertMany(rets);
// collection_to.update({}, {"$rename":{"time_line._id": "time_line.time"}})
// As mentioned in the documentation there is no way to rename fields within arrays.
// Your only option is to iterate over your collection documents, read them and update each with $unset old/$set new operations.