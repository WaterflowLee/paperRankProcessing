var client = new Mongo();
var db = client.getDB("paper_rank");
var collection_from = db.papers
var collection_to = db.rank
var cnt = 0;
var rets = [];
var ps = collection_from.find();
// var tic = new Date().getTime();
while(ps.hasNext()){
	var p = ps.next();
	var p_rank = {};
	var keys = Object.keys(p.loss_value);
	for (var k_index in keys){
		var key = keys[k_index];
		var lv = p["loss_value"][key];
		var field = "loss_value." + key;
		rank = collection_from.find({[field]: {"$gt": lv}}).count() + 1;
		p_rank[key] = rank;
	}
	rets.push({"_id": p["_id"], "rank": p_rank});
	if (cnt%200 === 0){
		collection_to.insertMany(rets);
		rets = [];
		// var toc = new Date().getTime();
		// print(toc - tic);
		print(cnt);
	}
	cnt += 1;
	// if (cnt===6){
	// 	break;
	// }
}