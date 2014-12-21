var tree_act=tree_click;
function citem(title,url,icon){
   //icon='http://img.wdian.net/scripts/webfx/images/org.gif';
   var e=new WebFXTreeItem(title);
   if(url!=''){
   	e.action='javascript:tree_act(\''+title+'\',\''+url+'\',\''+icon+'\');';
   }
   return e;
}

if (document.getElementById) {
	var tree = new WebFXTree('合作商管理系统');
	tree.setBehavior('classic');

	var a1=citem('系统设置','','');
	tree.add(a1);
	a1.add(citem('分店管理','index?m=subm&act=list',''));
	a1.add(citem('菜谱分类管理','index?m=food&act=category',''));
	a1.add(citem('菜谱管理','index?m=food&act=foods&cid=-1',''));
	
	var a2=citem('信息设置','','');
	tree.add(a2);
	a2.add(citem('设置公告','index?m=page&act=update&type=notice',''));
	a2.add(citem('修改商家介绍','index?m=page&act=update&type=about',''));
	
	var a=citem('订单管理','','');
	tree.add(a);
	a.add(citem('未处理订单','index?m=order&act=list&status=0',''));
	a.add(citem('处理中订单','index?m=order&act=list&status=1',''));
	a.add(citem('配送中订单','index?m=order&act=list&status=2',''));
	a.add(citem('已完成订单','index?m=order&act=list&status=3',''));
	a.add(citem('已作废订单','index?m=order&act=list&status=-1',''));
	
	
	var a3=citem('帮助','','');
	tree.add(a3);
	a3.add(citem('官方网站','http://www.ops.cc/?from=wdian',''));

	document.getElementById('nav').innerHTML='<div style="padding:10px">'+tree+'</div>';
}
