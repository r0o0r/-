from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
# Create your views here.

@csrf_exempt
def test(request):
    data = json.loads(request.body)
    print(data.get('ques'))
    return JsonResponse({'info': 'ok'})

@csrf_exempt
def home(request):
    data = json.loads(request.body)
    q = data.get('ques')
    if q == '你好':
        answer = '你好'
    else:
        answer = '我是一条回答'
    return JsonResponse({'answer': answer})

@csrf_exempt
def graph(request):
    question = request.GET.get('ques')
    print(question)
    medical_graph = Graph("http://localhost:7474", auth=("neo4j", "li20020516"))
    ques = {'entity_type': '疾病', 'name': ['急性呼吸窘迫综合征'], 'relation': ['症状', '推荐食谱']}
    nodes = []
    links = []
    length = len(ques['name'])
    categories = list(medical_graph.schema.node_labels)
    final_categories = []
    for category in categories:
        if category == ques['entity_type']:
            final_category = {'category': category, 'num': str(length), 'name': category}
        else:
            final_category = {'category': category, 'num': '0', 'name': category}
        final_categories.append(final_category)
    if not question:
        return JsonResponse({'nodes': nodes, 'links': links, 'categories': final_categories})
    for name in ques['name']:
        node = {'name': name, 'des': name, 'symbolSize': 40, 'category': categories.index(ques['entity_type'])}
        nodes.append(node)
        for relation in ques['relation']:
            data = medical_graph.run("match(a:`%s`{`名称`:'%s'})-[n:`%s`]-(b) return n.名称,b.名称,labels(b)" % (
            ques['entity_type'], name, relation)).data()
            if data:
                length = 0
                for d in data:
                    node = {'name': d['b.名称'], 'des': d['b.名称'], 'symbolSize': 40,
                            'category': categories.index(d['labels(b)'][0])}
                    length = length + 1
                    link = {'source': name, 'target': d['b.名称'], 'name': d['n.名称'], 'des': d['n.名称']}
                    nodes.append(node)
                    links.append(link)
                for cate in final_categories:
                    print(cate['category']==data[0]['labels(b)'][0])
                    if cate['category'] == data[0]['labels(b)'][0]:
                        cate['num'] = str(length)
                        break
    for cate in final_categories:
        cate['name'] = cate['category'] + cate['num']
    print(final_categories)
    return JsonResponse({'nodes': nodes, 'links': links, 'categories': final_categories})