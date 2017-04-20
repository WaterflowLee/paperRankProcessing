var client = new Mongo();
var db_from = client.getDB("helper");
var db_to = client.getDB("paper_rank");
var collection_to = db_to.papers_top_NW;
for (var start=1871;start<=1986;start++){
	var end = start + 30;
	var collection_from = "From_" + start + "_to_" + end;
	var cursor = db_from[collection_from].find();
	while(cursor.hasNext()){
		var p = cursor.next();
		var key = "loss_value." + (30 - ( p["time"] - start ));
		var setting = {};
		setting[key] = p["loss_value"];
		collection_to.updateOne({"_id":p["_id"]}, {"$set":setting});
	}
	print("Finished: " + start + " to " + end);
}