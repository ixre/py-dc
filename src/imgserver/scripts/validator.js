/*
 * js validator 0.1
 * 
 * author : newmin
 *    www.ops.cc
 */
var valid=new Object({
    $:function(id){return document.getElementById(id);},
    setError:function(ele,index){
                var _reg=eval('/^([\\u4e00-\\u9fa5]+)\\{[A-Za-z\\u4e00-\\u9fa5\\d:,-]*'+index+':([A-Za-z\\u4e00-\\u9fa5\\d,-]+)(\\d)*[A-Za-z\\u4e00-\\u9fa5\\d:,-]*\\}/');
                var msg=ele.getAttribute('err');
                if(msg!=null){
                	msg=msg.replace(_reg,"$1$2");
                	var _idx=msg.indexOf(',');
                	if(_idx!=-1)msg=msg.substring(0,_idx);
                	//处理错误
                	valid.displayError(ele,msg);
                }
            },
    displayError:function(ele,msg){
               ele.parentNode.getElementsByTagName("span")[0].innerHTML="<em class='valid_error'>"+msg+"</em>";;
                return false;
            },
    displayRight:function(ele,msg){
               ele.parentNode.getElementsByTagName("span")[0].innerHTML="<em class='valid_right'>"+(msg||'&nbsp;')+"</em>";
            },
    clear:function(ele,msg){
        ele.parentNode.getElementsByTagName("span")[0].innerHTML="";
    },
    setErrorFocus:function(error){
        var inputs=error.parentNode.parentNode.getElementsByTagName('input');
        if(inputs.length!=0){
            inputs[0].focus();
        }
    },
    check:function(panel){
    	var result=true;
    	var sps=panel.getElementsByTagName('SPAN');
     
    	for(var i=0;i<sps.length;i++){
    		var arr=sps[i].getElementsByTagName('EM');
    		if(arr.length<1 || arr[0].className=='valid_error'){
    			result=false;
    		}
    	}
    	return result;
    }
});
