from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from testcase_app.models import Testcase
import requests
import json

# 用例列表页
@login_required
def testcase_list(request): 
	# project_all = Project.objects.all()
	return render(request,"testcase.html",{"type":"list"})

# 
@login_required
def debug(request):

	if request.method == "POST":
		url = request.POST.get("url","")
		req_method = request.POST.get("method","")
		req_header = request.POST.get("header","")
		para_type = request.POST.get("type","")
		parameters = request.POST.get("parameter","")
		
		try:
			parameters=parameters.replace("\'","\"")
			payload = json.loads(parameters)#json str -> dict
		except json.decoder.JSONDecodeError as e:
			return JsonResponse({"result":"请求参数错误","status":"error"})

		# try:
		# 	print("req_header",req_header)
		# 	req_header=req_header.replace("\'","\"") 
		# 	req_header = json.loads(req_header)#json str -> dict
		# 	print("req_header",req_header)
		# except json.decoder.JSONDecodeError as e:
		# 	return JsonResponse({"result":"请求头类型错误","status":"error"})

		if req_method == "get":
			r = requests.get(url,params=payload)

		if req_method == "post":
			if para_type == "form":
				r = requests.post(url,data=payload)
			if para_type == "json":
				r = requests.post(url,json=payload)
				# or
				# r = requests.post(url,headers=req_header,data=parameters)
		return JsonResponse({"result":r.text,"status":"success"})
	else:
		return JsonResponse({"result":"请求方式错误"})

# 
@login_required
def assert_result(request):

	if request.method == "POST":
		req_result = request.POST.get("req_result","")
		assert_type = request.POST.get("assert_type","")
		input_assert = request.POST.get("input_assert","")
		print("req_result",req_result)
		print("assert_type",assert_type)
		print("input_assert",input_assert)

		if input_assert == "" or req_result == "":
			return JsonResponse({"result":"断言文本不能为空","status":"error"})

		if assert_type == "contains":
			if input_assert in req_result:
				return JsonResponse({"result":"断言成功","status":"success"})

		if assert_type == "all":
			if input_assert == req_result:
				return JsonResponse({"result":"断言成功","status":"success"})

		return JsonResponse({"result":"断言失败","status":"success"})

	else:
		return JsonResponse({"result":"请求方式错误"})


# 创建用例
@login_required
def add_testcase(request):
	if request.method == "GET":
		return render(request,"testcase.html",{"type":"add"})
	elif request.method == "POST":
		name = request.POST.get("name","")
		describe = request.POST.get("describe","")
		status = request.POST.get("status","")
		if name == "":
			return render(request,"testcase.html",{"type":"add","name_error":"项目名称不能为空"})
		p = Project.objects.create(name=name,describe=describe,status=status)
		p.save()
		return HttpResponseRedirect("/testcase/")

# 编辑用例
@login_required
def edit_testcase(request,tid):
	# print("--edit_project--method:" + request.method)
	if request.method == "GET":
		p = Project.objects.get(id=pid)
		form = ProjectForm(instance=p)
		return render(request,"project.html",{"type":"edit","form":form,"pid":pid})
	
	elif request.method == "POST":
		form = ProjectForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			describe = form.cleaned_data['describe']
			status = form.cleaned_data['status']
			p = Project.objects.get(id=pid)
			p.name = name
			p.describe = describe
			p.status = status
			p.save()
			return HttpResponseRedirect("/project/")
		else:
			return HttpResponse("Wrong")


# 删除用例
@login_required
def delete_testcase(request,tid):
	if request.method == "GET":
		p = Project.objects.filter(id=pid)
		p.delete()
		return HttpResponseRedirect("/project/")
	else:
		return HttpResponseRedirect("/project/")

# 保存用例
@login_required
def save_case(request):
	if request.method == "POST":

		url = request.POST.get("url","")
		req_method = request.POST.get("method","")
		header = request.POST.get("header","")
		parameter_type = request.POST.get("type","")
		parameter = request.POST.get("parameter","")
		mid = request.POST.get("mid","")
		assert_type = request.POST.get("assert_type","")
		assert_text = request.POST.get("assert","")
		case_name = request.POST.get("case_name","")

		if case_name == "":
			return JsonResponse({"data":"用例名称不能为空","status":10101})
		
		if url == "":
			return JsonResponse({"data":"请求地址不能为空","status":10102})
		
		if req_method == "get":
			req_method = 1
		elif req_method == "post":
			req_method = 2
		elif req_method == "put":
			req_method = 3
		elif req_method == "delete":
			req_method = 4
		else:
			return JsonResponse({"data":"请求方式错误","status":10103})

		if parameter_type == "form":
			parameter_type = 1
		elif parameter_type == "json":
			parameter_type = 2
		else:
			return JsonResponse({"data":"参数类型错误","status":10103})
		
		if mid == "":
			return JsonResponse({"data":"所属模块不能为空","status":10104})

		if case_name == "":
			return JsonResponse({"data":"用例名称不能为空","status":10101})

		if assert_type == "contains":
			assert_type = 1
		elif assert_type == "match":
			assert_type = 2
		else:
			return JsonResponse({"data":"断言类型错误","status":10105})
		
		if assert_text == "":
			return JsonResponse({"data":"断言内容不能为空","status":10106})

		Testcase.objects.create(name=case_name,url=url,method=req_method,header=header,
			parameter_type=parameter_type,parameter_body=parameter,assert_result=result,
			assert_type=assert_type,assert_text=assert_text)
		
		return JsonResponse({"data":"创建成功","status":10200})
	else:
		return JsonResponse({"data":"请求方式错误","status":10400})