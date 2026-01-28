import sys
from gamspy import Container, Set, Parameter, Variable, Equation, Model, Sum, Sense

m = Container()

i = Set(container=m, name="i", description="plants")
j = Set(container=m, name="j", description="markets")


a = Parameter(
    container=m,
    name="a",
    domain=i,
    description="supply of commodity at plant i"
)

b = Parameter(
    container=m,
    name="b",
    domain=j,
    description="demand for commodity at market j"
)

c = Parameter(
    container=m,
    name="c",
    domain=[i,j],
    description="cost per unit of shipment between plant i and market j"
)

x = Variable(
    container=m,
    name="x",
    domain=[i,j],
    type="positive",
    description="camount of commodity to ship from plant i to market j"
)

supply = Equation(
    container=m,
    name="supply",
    domain=i,
    description="observe supply limit at plant i"
)

supply[i] = Sum(j, x[i,j])<=a[i]


demand = Equation(
    container=m,
    name="demand",
    domain=j,
    description="satisfy demand at market j"
)

demand[j] = Sum(i, x[i,j])>=b[j]

obj = Sum((i,j), c[i,j] * x[i,j])

transport = Model(
    container=m,
    name="transport",
    equations=[supply,demand],
    problem="LP",
    sense=Sense.MIN,
    objective=obj
)

i.setRecords(['seattle', 'san-diego'])

j.setRecords(['new-york', 'chicago', 'topeka'])

a.setRecords([('seattle', 350), ('san-diego', 600)])

b.setRecords([('new-york', 325), ('chicago', 300), ('topeka', 275)])

distances = [
    ['seattle', 'new-york', 2.5],
    ['seattle', 'chicago', 1.7],
    ['seattle', 'topeka', 1.8],
    ['san-diego', 'new-york', 2.5],
    ['san-diego', 'chicago', 1.8],
    ['san-diego', 'topeka', 1.4],

]

d = Parameter(
    container=m,
    name="d",
    domain=[i,j],
    records=distances,
    description="distance in thousands of miles"
)

c[i,j]= 90 * d[i,j] / 1000

transport.solve(output=sys.stdout)