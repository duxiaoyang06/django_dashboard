# from django.shortcuts import render
# from feedback.models import Info
# # Create your views here.
# def get_all_feedback(request):
# 	feedbacks={'f500': Info.objects.filter(status_code=500).count(),'f501':Info.objects.filter(status_code=501).count()
# 		,'f502':Info.objects.filter(status_code=502).count(),'f503':Info.objects.filter(status_code=503).count()}
#
# 	return render(request, 'feedback.html', {'feedbacks':feedbacks})