var client = new Mongo();
var db = client.getDB("paper_rank");
var cursor = db.papers.find();

var cal_marginal = function (paper) {
	var ref_loss_list = [];
	paper["reference"].forEach(
		function (ref) {
			var ret = db.papers.findOne({"_id":ref}, {"_id":0, "loss_value":1});
			if (ret !== null){
				var ref_loss = ret["loss_value"];
				ref_loss_list.push(ref_loss);
			}
			else{
				print("This ref is not in our scope(database)!");
			}
		}
	);
	// printjson(ref_loss_list);
	// print(ref_loss_list===[]);
	// print(ref_loss_list===new Array());
	ref_loss_avg = {};
	ref_loss_margianl = {};
	for(var key in paper["loss_value"]){
		if (paper["loss_value"].hasOwnProperty(key)){
			if (ref_loss_list.length !== 0){
				var sum=0;
				var counter=0;
				ref_loss_list.forEach(
					function (ref_loss) {
						sum += ref_loss[key];
						counter++;
					}
				);
				ref_loss_avg[key] = sum/counter;
			}
			else{
				ref_loss_avg[key] = 1.0;
			}
			ref_loss_margianl[key] = paper["loss_value"][key]/ref_loss_avg[key];
		}
	}
	return ref_loss_margianl;
};
var c=0;
while(cursor.hasNext()){
	var paper = cursor.next();
	var marginal_loss_value = cal_marginal(paper);
	db.papers.updateOne({"_id":paper["_id"]}, {"$set":{"marginal_loss_value":marginal_loss_value}});
	if(c%100){
		print("Finish "+c);
	}
	c++;
}