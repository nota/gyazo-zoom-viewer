//
// var data = [
//   ["19950327000100", "40986c4c4a309ecca49edacfdf8d8798", 33.1013202640288, 131.223277042406, "建斗", "九州旅行でやまなみハイウェイドライブ中に山を登ったとき"],
//   ["19960820000100", "16a945c8d6b311160ae7f727b4f97efe", 35.6259460468893, 139.730376512521, "原田", null],
//   ["19970221000100", "89b3a210f014df14bf5f583ae6c4a99b", 35.6481223540639, 140.036424240918, null, null],
//   ["19970221000101", "7a821beb3354a04ef1298b59d73376c5", null, null, "大平 徹", null],

//  ["20130206042624", "5404299d636a303fa38b85d54f93979b", "", 35.23, 139.34, "SIM, 電話, 携帯", ""],
//

//
// URLから引数を取得
// e.g. index.html?q=名山
//      index.html#名山
//

let query = null
let h = window.location.href.split(/#/)
if(h.length > 1){
    query = decodeURIComponent(h[1])
}
else {
    let argstr = window.location.search.substring(1,window.location.search.length)
    let args = argstr.split(/&/)
    for(let i=0;i<args.length;i++){
	let a = args[i].match(/q=(.*)/)
	if(a){
	    query = decodeURIComponent(a[1])
	}
    }
}

// var ignoreNextZoom = false; // 汚いハック... これがtrueのときはGoogleMaps上での次のズームイベントを無視する

function searchFunc(keyword){
    return function(){
	history.pushState(keyword, keyword, "#"+keyword)
	keywordSearchAndDisplay(keyword)
    }
}

function photoDiv(rainbowzoomer){ // 写真を表示するdivを生成
    let div = document.createElement('div')
    let image = document.createElement('img')
    image.src = this.gyazourl
    //image.style.width = "120px"
    image.style.maxWidth = "120px"
    image.style.maxHeight = "90px"
    div.style.position = "absolute"
    div.style.left = this.left
    div.style.top = this.top + rainbowzoomer.offset
    div.style.margin = "2"
    this.width = 120
    div.appendChild(image)
    image.rainbowzoomer = rainbowzoomer
    div.rainbowzoomer = rainbowzoomer
    return div
}

function photoSize(entry){
    let size = {}
    size.width = 130.0
    size.height = 100.0
    return size
}

function initPhotoData(){
    let index = 0
    let yentry, mentry, dentry
    let entry

    //let startyear = Number(data[0].str.match(/^\d{4}/)[0])
    //let lastyear = Number(data[data.length-1].str.match(/^\d{4}/)[0])
    let lastyear = Number(data[0].str.match(/^\d{4}/)[0])
    let startyear = Number(data[data.length-1].str.match(/^\d{4}/)[0])

    let hideocr = document.getElementById("hideocr").checked
    let commentedonly = document.getElementById("commentedonly").checked

    //for(let year=startyear;year<=lastyear;year++){
    for(let year=lastyear;year>=startyear;year--){
	entry = {}
	entry.str = year.toString()
	entry.indent = 0
	entries.push(entry)
	yentry = entry;
	yentry.count = 0;
	//for(var month=1;month<=12;month++){
	for(var month=12;month>=1;month--){
	    entry = {}
	    entry.str = year.toString() + "/" + month.toString()
	    entry.indent = 1
	    entries.push(entry)
	    mentry = entry
	    mentry.count = 0
	    days = mdays(year,month)
	    //for(let day=1;day<=days;day++){
	    for(let day=days;day>=1;day--){
		entry = {}
		entry.str = year.toString() + "/" + month.toString() + "/" + day.toString()
		entry.indent = 2
		entries.push(entry)
		dentry = entry
		dentry.count = 0
		let daystr = "" + year + ("0"+month).slice(-2) + ("0"+day).slice(-2); // これと比較する
		//while(index < data.length && data[index].str.slice(0,8) < daystr){
		while(index < data.length && data[index].str.slice(0,8) > daystr){
		    index += 1
		}
		while(index < data.length && data[index].str.slice(0,8) == daystr){
		    //entry = data[index]
		    if(hideocr && data[index] && data[index].comment && data[index].comment.length > 400){
		    }
		    else if(commentedonly && data[index] && (data[index].usercomment == "" || typeof data[index].usercomment === "undefined")){
			// コメントが無いものは非表示
			// ブクマしたものはコメントを書くようにする
		    }
		    else {
			entry = {}
			// entry.str = data[index].str
			entry.id = data[index].id
			entry.url = data[index].url
			entry.gyazourl = data[index].gyazourl
			entry.keywords = data[index].keywords
			entry.description = data[index].description
			entry.comment = data[index].comment
			entry.title = data[index].title
			
			//entry.str = daystr ////////////////////
			entry.str = `${year}/${month}/${day}`
			entry.indent = 3
			entry.div = photoDiv
			entry.size = photoSize
			yentry.count += 1
			mentry.count += 1
			dentry.count += 1
			entries.push(entry)
		    }
		    index += 1
		}
	    }
	}
    }
    // 写真が無い日付は削除
    for(let i=0; i < entries.length; ){
	if(entries[i].count == 0){
	    entries.splice(i,1)
	}
	else {
	    i += 1
	}
    }
    // 日付に対応した写真枚数を追加
    for(let i=0;i<entries.length;i++){
	let entry = entries[i]
	if(entry.indent <= 2){
	    entry.str += (" (" + entry.count + "枚)")
	}
    }
}

var entries = [];     // 日付/写真など全データの配列
var tmpentries;
var photoZoomer;

var expanded = false;

var kwentries = [];
var keywordZoomer;

document.getElementById("hideocr").addEventListener("change",function(){
    init()

    let query = document.getElementById("query").value
    if(query != ""){
	keywordSearchAndDisplay(query)
    }
})

document.getElementById("commentedonly").addEventListener("change",function(){
    init()

    let query = document.getElementById("query").value
    if(query != ""){
	keywordSearchAndDisplay(query)
    }
})

function init(){
    entries = []

    // RainbowZoomerで表示するための写真データ初期化
    initPhotoData();

    let photodiv = document.getElementById('photos')
    let width = window.innerWidth
    // if(width > 720) width = 720
    photodiv.style.width = width - 10
    let height = window.innerHeight
    photodiv.style.height = height - 60
    
    let centerline = document.getElementById('centerline')
    centerline.style.width = width - 10

    photoZoomer = new RainbowZoomer(photodiv,entries);
    photoZoomer.setClickZoom(false);
    photoZoomer.setGranularity(13);
    photoZoomer.update(photoZoomer.maxDOI + 1.0); /////

    // 検索語からマッチ計算
    q = (query ? query : 'verystrangesearchstring');
    // q = (query ? query : '');

    keywordSearchAndDisplay(q);

    // 「戻る」ボタンで前の状態に戻す!
    window.addEventListener("popstate", function(event){
	    q = (event.state ? event.state : '名山');
	    keywordSearchAndDisplay(q);
    }, false);

}

//
// キーワードからの検索
//
function keywordMatch(q){
    // alert(`keywordMatch(${q})`)
    let count = 0
    let upq = q.toUpperCase()
    expanded = false
    for(let i=0;i<entries.length;i++){
	let entry = entries[i]
	entry.matched = false
	//keywords = entry.keywords;
	//if(keywords){
	//    a = keywords.split(/, */);
	//    for(var j=0;j<a.length;j++){
	//	var keyword = a[j];
	//	if(keyword == q){
	//	    entry.matched = true;
	//	    break;
	//	}
	//    }
	//}
	if((entry.comment && entry.comment.toUpperCase().indexOf(upq) >= 0) ||
	   (entry.description && entry.description.toUpperCase().indexOf(upq) >= 0) ||
	   (entry.title && entry.title.toUpperCase().indexOf(upq) >= 0) ||
	   (entry.keywords && entry.keywords.toUpperCase().indexOf(upq) >= 0)){
	    entry.matched = true
	    count += 1
	}
    }
}

function keywordSearchAndDisplay(q){
    keywordMatch(q);

    // RainbowZoomer表示
    photoZoomer.update(q == "verystrangesearchstring" ? photoZoomer.maxDOI + 1.0 : 6.0);

    // alert(document.getElementById("hideocr").checked)
}

function dynamicquery(){
    let query = document.getElementById("query").value
    if(query == ""){
	query = "verystrangesearchstring"
    }
    keywordSearchAndDisplay(query)
}
