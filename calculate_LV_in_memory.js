// jQuery isEmptyObject 的实现
function isEmptyObject(obj) {
	for (var key in obj) {
		return false;
	}
	return true;
}
var constructList = function(start, end){
	var need_to_cal = {};
	var just_init = {};
	var cursor = collection_from.find({"time":{"$gte":start,"$lt":end}, "citations":{"$exists":1}},
		{"_id":1, "eigen":1, "time":1, "reference_normalized_weights":1, "citations":1}).sort({"time":1});
	while(cursor.hasNext()){
		var p = cursor.next();
		p.ready = false;
		p.wait = false;
		p.loss_value = p.eigen;
		need_to_cal[p["_id"]] = p;
	}
	cursor = collection_from.find({"time":{"$gte":start,"$lt":end}, "citations":{"$exists":0}},
		{"_id":1, "eigen":1, "time":1, "reference_normalized_weights":1});
	while(cursor.hasNext()){
		var q = cursor.next();
		q.ready = true;
		q.wait = false;
		q.loss_value = q.eigen;
		just_init[q["_id"]] = q;
	}
	return [need_to_cal, just_init];
};
// 有的文档有 citations, 因此能够进到 need_to_cal 中, 
// 但是其 citations 并没有在这个 interval 中(不在 need_to_cal 和 just_init 中),
// 不在 need_to_cal会导致 canCal 返回 true ,进入cal中
// 不在 just_init 会导致 cal 返回的sum是0, 并最终导致 add 0
var canCal = function (need_to_cal, _id) {
	if (need_to_cal.hasOwnProperty(_id)){
		var citations = need_to_cal[_id].citations;
		for(var c in citations){
			var c_id = citations[c];
			var ret = need_to_cal.hasOwnProperty(c_id);
			if (ret === true){
				return false;
			}
		}
		return true;
	}
	else{
		print("Fatal error!");
	}
};
var cal = function (need_to_cal, just_init, _id){
	var citations = need_to_cal[_id].citations;
	var sum = 0;
	for(var c in citations){
		var c_id = citations[c];
		// var citation = just_init[c_id] || need_to_cal[c_id];
		var citation = just_init[c_id];
		if (citation !== undefined){
			sum += citation["reference_normalized_weights"][_id] * citation["loss_value"];
		}
	}
	return sum;
};
function pickUpOne(need_to_cal){
	for(var key in need_to_cal){
		if (need_to_cal[key].wait === false){
			return need_to_cal[key];
		}
	}
	if (isEmptyObject(need_to_cal)){
		return undefined;
	}
	return false;
}
function breakLoop(need_to_cal, just_init, waitList){
	var minum = 1000000;
	var kOfMinum = "";
	for (var k in need_to_cal){
		if (need_to_cal.hasOwnProperty(k)){
			if (need_to_cal[k].time < minum){
				minum = need_to_cal[k].time;
				kOfMinum = k;
			}
		}
	}
	need_to_cal[kOfMinum].ready = true;
	resetWaitState(need_to_cal, waitList);
	just_init[kOfMinum] = need_to_cal[kOfMinum];
	delete need_to_cal[kOfMinum];
}
function resetWaitState(need_to_cal, waitList){
	waitList.forEach(function(_id){
		need_to_cal[_id].wait = false;
	});
	// waitList = [];形参 waitList 原来是指向外部的 waitList的, 
	// 这样仅仅是给形参 waitList 换了一个引用指向了[], 外部的 waitList 并没有被清空
	// 应该如此不换引用地清空
	waitList.splice(0, waitList.length);
}
var calForAnInterval = function (need_to_cal, just_init){
	var waitList = [];
	while(!isEmptyObject(need_to_cal)){
		var cur = pickUpOne(need_to_cal);
		if (cur === false){
			breakLoop(need_to_cal, just_init, waitList);
			print("Break loop!");
		}
		else if (cur !== undefined){
			if (canCal(need_to_cal, cur["_id"])){
				var sum = cal(need_to_cal, just_init, cur["_id"]);

				need_to_cal[cur["_id"]].loss_value += sum; 
				need_to_cal[cur["_id"]].ready = true;
				resetWaitState(need_to_cal, waitList);
				just_init[cur["_id"]] = need_to_cal[cur["_id"]];
				delete need_to_cal[cur["_id"]];

				if(VERBOSE){
					print("update " + cur["_id"] + "'s loss value by adding " + sum);
				}
			}
			else{
				need_to_cal[cur["_id"]].wait = true;
				waitList.push(cur["_id"]);
				if(VERBOSE){
					// print("let " + cur["_id"] + " wait!");
				}
			}
		}
	}
};

var VERBOSE = true;
var client = new Mongo();
var db_from = client.getDB("paper_rank");
var collection_from = db_from.papers_top_NW;
var db_to = client.getDB("helper");

// 为了用上所有的论文,时间跨度应该是start[1871,1986] 1871:第一次用上1900年的;1986:第一次用上2015年的.
for(var start=1871;start<=1986;start++){
	var collection_to = "From_" + String(start) + "_to_" +String(start+30); 
	// 这是一个特别的SB的地方, 数据被写进了一个叫做 collection_to 的集合中而不是From ...
	// db_to.collection_to.drop();
	db_to[collection_to].drop();
	var ls = constructList(start, start+30);
	need_to_cal = ls[0];
	just_init = ls[1];
	// printjson(just_init[Object.keys(just_init)[1]]);
	calForAnInterval(need_to_cal, just_init);

	var just_init_array = [];
	// 字面对象没有 forEach
	// just_init.forEach(function (key){
	// 	just_init_array.push(just_init[key]);
	// });
	for (var k in just_init){
		var p = just_init[k];
		just_init_array.push({
			"_id":p["_id"],
			"time":p["time"],
			"loss_value":p["loss_value"],
			"ready":p["ready"],
			"wait":p["wait"]
		});
	}
	db_to[collection_to].insertMany(just_init_array);
	print(start+ " To " + (start+30) + " finished!");
}
// Object.values(just_init) 
// This is an experimental technology
// Because this technology's specification has not stabilized, 
// check the compatibility table for usage in various browsers. 
// Also note that the syntax and behavior of an experimental technology is subject to change 
// in future versions of browsers as the specification changes.
// Object.keys()就没有这些!