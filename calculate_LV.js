var constructCollection = function(start, end){
	var need_to_cal = [];
	var just_init = [];
	var cursor = collection_from.find({"time":{"$gte":start,"$lt":end}, "citations":{"$exists":1}},{"_id":1, "eigen":1, "time":1});
	while(cursor.hasNext()){
		need_to_cal.push(cursor.next());
	}
	cursor = collection_from.find({"time":{"$gte":start,"$lt":end}, "citations":{"$exists":0}},{"_id":1, "eigen":1, "time":1});
	while(cursor.hasNext()){
		just_init.push(cursor.next());
	}
	// printjson(need_to_cal);
	// printjson(arr);
	// db_to.dropDatabase();
	var ready_state = "From_" + String(start) + "_to_" +String(end); 
	db_to[ready_state].drop();
	db_to[ready_state].insertMany(need_to_cal);
	db_to[ready_state].updateMany({},{"$set":{"ready":false}});
	db_to[ready_state].insertMany(just_init);
	db_to[ready_state].updateMany({"ready":{"$exists":0}},{"$set":{"ready":true}});
	db_to[ready_state].updateMany({}, {"$rename":{ "eigen": "loss_value" }, "$set":{"wait":false}});
	// cursor = db_to.ready_state.find();
	return db_to[ready_state]
};
// while(cursor.hasNext()){
// 	printjson(cursor.next());
// }
// cal 和 canCal 中的 null判断可以将不在interval中的citation剔除在外,即loss_value是有interval区别的而reference_normalized_weights
// 是一篇论文的固有属性，不会因为interval不同而不同.一个从前往后看一个从后往前看.
var canCal = function (_id) {
	var citations = collection_from.findOne({"_id":_id}, {"_id":0, "citations":1});
	for(var c in citations["citations"]){
		var c_id = citations["citations"][c];
		var ret = collection_to.findOne({"_id":c_id}, {"_id":0, "ready":1});
		if (ret !== null){
			var bool = ret["ready"];
			if (bool === false){
				return false;
			}
			if (VERBOSE){
				// print(c_id + " is  in this interval!");
			}
		}
		else{
			if(VERBOSE){
				// print(c_id + " is not in this interval!");
			}
		}
	}
	return true;
};
var cal = function (_id){
	var citations = collection_from.findOne({"_id":_id}, {"_id":0, "citations":1});
	var sum = 0;
	for(var c in citations["citations"]){
		var c_id = citations["citations"][c];
		var ret = collection_to.findOne({"_id":c_id}, {"loss_value":1});
		if (ret !== null){
			var nw = collection_from.findOne({"_id":c_id}, {"reference_normalized_weights":1})["reference_normalized_weights"][_id];
			sum += nw * ret["loss_value"];
		}
		else{
			if(VERBOSE){
				// print(c_id + " is not in this interval!");
			}
		}
	}
	return sum;
};
var calForAnInterval = function (){
	while(collection_to.findOne({"ready":false}, {"_id":1}) !== null){
		var cur = collection_to.find({"ready":false, "wait":false},{"_id":1}).sort({"time":1});
		if (!cur.hasNext()){
			//存在ready是false,且wait都是true,即需要计算的节点在互相等待,存在死锁,相互掣肘.
			var pipeline = [{"$match":{"ready":false,"wait":true}}, {"$project":{"min_time":{"$min":"$time"}}}];
			var min_time = collection_to.aggregate(pipeline).next()["min_time"];
			collection_to.updateOne({"ready":false,"wait":true,"time":min_time}, {"$set":{"ready":true}});
			collection_to.updateMany({"wait":true}, {"$set":{"wait":false}});
			print("Break loop!");
		}
		else{
			var ret = cur.next();
			if (canCal(ret["_id"])){
				var sum = cal(ret["_id"]);
				collection_to.updateOne({"_id":ret["_id"]}, {"$set":{"ready":true}, "$inc":{"loss_value":sum}});
				collection_to.updateMany({"wait":true},{"$set":{"wait":false}});
				if(VERBOSE){
					print("update " + ret["_id"] + "'s loss value by adding " + sum);
				}
			}
			else{
				collection_to.updateOne({"_id":ret["_id"]}, {"$set":{"wait":true}});
				if(VERBOSE){
					print("let " + ret["_id"] + " wait!");
				}
			}
		}
	}
};

var client = new Mongo();
var db_from = client.getDB("paper_rank");
var collection_from = db_from.papers_top_NW;
var db_to = client.getDB("helper");
var VERBOSE = true;
for(var start=1968;start<1985;start++){
	collection_to = constructCollection(start, start+30);
	calForAnInterval();
	print(start+ " To " + (start+30) + " finished!")
}