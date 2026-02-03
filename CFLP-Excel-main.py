import sys
import pandas as pd
from gamspy import Container, Set, Parameter, Variable, Equation, Model, Sum, Sense
from scgraph.geographs.us_freeway import us_freeway_geograph


# 1. Load Data
xl = pd.ExcelFile("data.xlsx")
df_i = xl.parse("Customers")
df_j = xl.parse("Facilities")

m = Container()

# 2. Sets
i = Set(m, name="i", records=df_i["i"], description="customers")
j = Set(m, name="j", records=df_j["j"], description="potential facilities")

# 3. Parameters (Coordinates)
lat_i = Parameter(m, name="lat_i", domain=i, records=df_i[["i", "lat"]])
lon_i = Parameter(m, name="lon_i", domain=i, records=df_i[["i", "lon"]])
lat_j = Parameter(m, name="lat_j", domain=j, records=df_j[["j", "lat"]])
lon_j = Parameter(m, name="lon_j", domain=j, records=df_j[["j", "lon"]])

# 4. Parameters (Demand and Capacity)
capacity = Parameter(m, name="capacity", domain=j, records=df_j[["j", "capacity"]])
demand = Parameter(m, name="demand", domain=i, records=df_i[["i", "demand"]])
f = Parameter(m, name="f", domain=j, records=df_j[["j", "f"]])

# 5. Calculate Cost/Distance Matrix (Euclidean)
c = Parameter(m, name="c", domain=[i, j])
c[i, j] = ((lat_i[i] - lat_j[j])**2 + (lon_i[i] - lon_j[j])**2)**0.5

# 6. Variables
x = Variable(m, name="x", domain=[i, j], type="positive")
y = Variable(m, name="y", domain=j, type="binary")

# 7. Equations
demand_cons = Equation(m, name="demand_cons", domain=i)
demand_cons[i] = Sum(j, x[i, j]) >= demand[i]

capacity_cons = Equation(m, name="capacity_cons", domain=j)
capacity_cons[j] = Sum(i, x[i, j]) <= capacity[j] * y[j]

# 8. Objective & Model
obj = Sum(j, f[j] * y[j]) + Sum((i, j), c[i, j] * x[i, j])

facility_loc = Model(
    container=m,
    name="facility_loc",
    equations=[demand_cons, capacity_cons],
    problem="MIP",
    sense=Sense.MIN,
    objective=obj
)

facility_loc.solve(output=sys.stdout)

# 9. Results
if facility_loc.status.value == "Normal Completion":
    print("\nOptimal Solution Found.")
    print("Facilities Open:\n", y.records[y.records['level'] > 0.5])
