var client = new Mongo();
var db = client.getDB("paper_rank");
// var collection = db.papers;
var collection = db.traditional_rank_table;
lv_key = "loss_value";
collection.createIndex({[lv_key]: -1});
