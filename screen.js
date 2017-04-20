var client = new Mongo();
var db = client.getDB("paper_rank");
var field = "loss_value.15";
var percent = 0.15;
var leftMiddleRight = function(papers_set, time) {
	var range = [time-1, time, time+1];
	var cursor = db.papers.find({"time":{"$in":range}}, {"_id":1}).sort({field:-1});
	cursor = cursor.limit(Math.round(cursor.count()*percent));
	while(cursor.hasNext()){
		papers_set.add(cursor.next()["_id"]);
	}
};
var papers_set = new Set();
for(var time=1900;time<=2015;time++){
	leftMiddleRight(papers_set, time);
}
print(papers_set.size)
papers_set.forEach(function(_id){
	var paper = db.papers.findOne({"_id":_id}, {"reference_normalized_weights":0, "marginal_loss_value":0, "citations":0, "loss_value":0});
	db.papers_top.insertOne(paper);
});
db.papers_top.update({},{"$pull":{"reference":{"$nin":papers_set.values()}}},{multi:true});