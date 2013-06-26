window.onload=initialize

var count=0;

function initialize()
{
	var tmp = document.getElementById("count_num");
	var count_str = tmp.innerHTML;
	count = parseInt(count_str);

}


function addFavorite()
{
	count++;
	var target=document.getElementById("dynamic_form_here");
	var TemO=document.getElementById("insert_here");
	var newInput = document.createElement("div");

	html = "<div class=\"row-sub\"><label class=\"my_label\" for=\"Favorite\" > Favorite"+count+" </label>";
	html+="<input class=\"sign_input2\" name=\"Favorite" +count+"\" placeholder=\"Enter your favorite product \"/></div>";			
				
        newInput.innerHTML = html;
	target.insertBefore(newInput,TemO);
	
	var newline= document.createElement("br");//创建一个BR标签是为能够换行！ 
	TemO.appendChild(newline); 	
	
}

function deleteFavorite()
{
	var target=document.getElementById("dynamic_form_here");
	var index="Favorite";
	index+=count.toString();
	var tmp=document.getElementById(index);
	
	target.removeChild(tmp);
	count--;
}
