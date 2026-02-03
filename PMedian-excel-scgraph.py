import sys
import pandas as pd
from gamspy import Container, Set, Parameter, Variable, Equation, Model, Sum, Sense
from scgraph.geographs.us_freeway import us_freeway_geograph


# Load Data
xl = pd.ExcelFile("data.xlsx")
df_i = xl.parse("Customers")
df_j = xl.parse("Facilities")

m = Container()

# Sets
i = Set(m, name="i", records=df_i["i"], description="customers")
j = Set(m, name="j", records=df_j["j"], description="potential facilities")

# Parameters (Coordinates)
lat_i = Parameter(m, name="lat_i", domain=i, records=df_i[["i", "lat"]])
lon_i = Parameter(m, name="lon_i", domain=i, records=df_i[["i", "lon"]])
lat_j = Parameter(m, name="lat_j", domain=j, records=df_j[["j", "lat"]])
lon_j = Parameter(m, name="lon_j", domain=j, records=df_j[["j", "lon"]])

# Parameters (Demand and P)
w = Parameter(m, name="w", domain=i, records=df_i[["i", "demand"]], description="weight/demand of customer i")
p_num = Parameter(m, name="p_num", description="number of facilities to locate")
p_num[...] = 5

# Calculate Cost/Distance Matrix (Euclidean)
d = Parameter(m, name="d", domain=[i, j], description="distance between i and j")

for i_idx, ci in df_i.iterrows():
    for j_idx, fj in df_j.iterrows():
        origin_node = {"latitude": float(ci["lat"]), "longitude": float(ci["lon"])}
        destination_node = {"latitude": float(fj["lat"]), "longitude": float(fj["lon"])}

        path_result = us_freeway_geograph.get_shortest_path(
            origin_node=origin_node,
            destination_node=destination_node,
            output_units="mi"  # or 'km'
        )

        d[ci["i"], fj["j"]] = path_result["length"]


# Variables
x = Variable(m, name="assign", domain=[i, j], type="binary", description="assignment of i to j")
y = Variable(m, name="locate", domain=j, type="binary", description="site selection")

# Equations
one_site = Equation(m, name="one_site", domain=i, description="each customer assigned once")
one_site[i] = Sum(j, x[i, j]) == 1

bound = Equation(m, name="bound", domain=[i, j], description="assignment bound by location")
bound[i, j] = x[i, j] <= y[j]

count = Equation(m, name="count", description="limit total facilities to p")
count[...] = Sum(j, y[j]) == p_num

# Objective
obj = Sum((i, j), w[i] * d[i, j] * x[i, j])

p_median = Model(
    container=m,
    name="p_median",
    equations=[one_site, bound, count],
    problem="MIP",
    sense=Sense.MIN,
    objective=obj
)



p_median.solve(output=sys.stdout)
