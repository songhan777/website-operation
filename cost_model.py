import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Planning inputs; USD quotes are checked separately in the report.
fx = 7.0
light = {'input': 0.20, 'output': 1.20}
strong = {'input': 2.0, 'output': 12.0}
mix = 0.15
pi = ((1-mix)*light['input']+mix*strong['input'])*fx
po = ((1-mix)*light['output']+mix*strong['output'])*fx
call_cost = (2000*pi+800*po)/1e6
task_cost = call_cost*1.1
aux = 0.003
scenarios = []
for name, mau, infra, labor, growth, admin, startup in [
    ('验证期', 1000, 500, 8000, 2000, 300, 50000),
    ('商业初期', 10000, 2000, 30000, 10000, 1000, 180000),
    ('增长期', 100000, 12000, 100000, 60000, 5000, 600000),
]:
    q = mau*20
    ai = q*task_cost
    ancillary = q*aux
    tech = ai+ancillary+infra
    fixed = labor+growth+admin
    operate = tech+fixed
    reserve = tech*.2
    scenarios.append(dict(name=name,mau=mau,tasks=q,ai=ai,ancillary=ancillary,infra=infra,
       tech=tech,labor=labor,growth=growth,admin=admin,operate=operate,reserve=reserve,
       budget=operate+reserve,startup=startup,year1=startup+12*(operate+reserve),
       runway6=startup+6*(operate+reserve)))
optim = [
    ('全部使用较高价模型',200000*1.1*(2000*14+800*84)/1e6),
    ('85%轻量模型 15%较高价模型',200000*1.1*(2000*pi+800*po)/1e6),
    ('输入1400 输出650',200000*1.1*(1400*pi+650*po)/1e6),
    ('调用放大系数降至1.03',200000*1.03*(1400*pi+650*po)/1e6),
    ('30%缓存读 5%缓存写',200000*1.03*(1400*pi*(.65+.3*.1+.05*1.25)+650*po)/1e6),
]
sens = []
for name,q,i,o,k,s in [
    ('基准',200000,2000,800,1.1,.15),
    ('每人任务数翻倍',400000,2000,800,1.1,.15),
    ('平均调用数升至2',200000,2000,800,2,.15),
    ('平均输入升至10000',200000,10000,800,1.1,.15),
    ('平均输出升至2400',200000,2000,2400,1.1,.15),
    ('较高价模型占比50%',200000,2000,800,1.1,.5),
]:
    cost=q*k*(i*((1-s)*.2+s*2)*7+o*((1-s)*1.2+s*12)*7)/1e6
    sens.append([name,cost])
v = task_cost+aux
unit = dict(task_variable=v,paid_usage=100,free_usage=20,price=49,fee_rate=.01,mau=10000,paid_rate=.03)
unit['paid_variable']=100*v
unit['free_variable']=20*v
unit['paid_contribution']=49*.99-100*v
unit['per_mau_contribution']=.03*unit['paid_contribution']-.97*unit['free_variable']
unit['tasks']=10000*(.03*100+.97*20)
unit['contribution']=10000*unit['per_mau_contribution']
unit['fixed']=43000
unit['profit']=unit['contribution']-unit['fixed']
unit['breakeven_mau']=unit['fixed']/unit['per_mau_contribution']
unit['minimum_paid_rate']=unit['free_variable']/(unit['paid_contribution']+unit['free_variable'])
unit['needed_paid_rate_at_10k']=(unit['fixed']/10000+unit['free_variable'])/(unit['paid_contribution']+unit['free_variable'])
result=dict(fx=fx,blended_input_cny=pi,blended_output_cny=po,call_cost=call_cost,task_cost=task_cost,
    scenarios=scenarios,optimization=optim,sensitivity=sens,unit=unit)
assert abs(task_cost-.0246092)<1e-10
assert all(abs(x['budget']-x['operate']-x['reserve'])<1e-8 for x in scenarios)
(ROOT/'model_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
