from datetime import date, datetime
from decimal import Decimal

from pony.orm import *

class District(Entity):
    name = Unique(unicode)
    shops = Set('Shop')

class Shop(Entity):
    name = Unique(unicode)
    address = Unique(unicode)
    district = Required(District)
    employees = Set('Employee')
    products = Dict('Product', 'Quantity')
    orders = Set('Order')

class Person(Entity):
    first_name = Required(unicode)
    last_name = Required(unicode)

class Employee(Person):
    date_of_birth = Required(date)
    salary = Required(Decimal)
    shop = Required(Shop)
    orders = Set(Order)

class Customer(Person):
    orders = Set(Order)

class ProductCategory(Entity):
    name = PrimaryKey(unicode)
    products = Set('Product')

class Product(Entity):
    name = Required(unicode)
    category = Required(ProductCategory)
    price = Required(Decimal)
    shops = Dict(Shop, 'Quantity')
    orders = Dict('Order', 'OrderItem')

class Quantity(Entity):
    shop = Required(Shop)
    product = Required(Product)
    quantity = Required(int)
    PrimaryKey(shop, product)

class Order(Entity):
    shop = Required(Shop)
    employee = Required(Employee)
    customer = Required(Customer)
    date = Required(datetime)
    total = Required(decimal)
    items = Dict(Product, 'OrderItem')

class OrderItem(Entity):
    order = Required(Order)
    product = Required(Product)
    price = Required(decimal)
    quantity = Required(decimal)
    # amount = Required(decimal)
    PrimaryKey(order, product)


# 1. ��������, ������������� � ���������� ������

select(s for s in Shop if s.district.name == u'����������')

# 2. �������, ���������� ������ � ���������� ������

select(c for c in Customer
         for s in Shop  if s.district.name == u'����������'
         for o in Order if o.customer == c and o.shop == s)
         
select(c for c in Customer
         for s in Shop
         for o in Order if o.customer == c and o.shop == s and s.district.name == u'����������')

select(o.customer for s in Shop if s.district.name == u'����������'
                  for o in s.order)

select(c for c in Customer
         if exists(o for o in c.orders if o.shop.district.name == u'����������'))

select(c for c in Customer
         if u'����������' in select(o.shop.district.name for o in c.orders))

select(c for c in Customer
         if u'����������' in select(o.shop.district.name for o in Orders
                                                         if o.customer == c))

select(c for c in Customer if u'����������' in c.orders.shop.district.name)
select(c for c in Customer if c.orders.shop.district.name.contains(u'����������'))

select(s for s in Shop if s.district.name == u'����������').orders.customer

# 3. ������, ����������� ������ � ����� ��������

select(p for p in Product if len(p.shops) == 1)  # �� ��������� ���� � Quantities ����������� quantity==0

select(p for p in Product if len(q.shop for q in Quantities
                                        if q.product == p and q.quantity > 0) == 1)

select(p for p in Product if len(q for q in p.shops.values()
                                   if q.quantity > 0) == 1)

select(q.product for q in Quantities if HAVING(COUNT(q.shop) == 1))

# 4. ����������, ���������� � ���������� ������

select(e for e in Employee if e.shop.district.name == u'����������')

# 5. ������, ������� ������ ��� �� ������

select(p for p in Product
         if p not in select(q.product for q in Quantities
                                      if q.quantity > 0))

select(p for p in Product
         if not exists(q for q in Quantities
                         if q.product == p and q.quantity > 0))

# 6. ������, ������� ���� �� ���� ���������

select(p for p in Product
         if len(s for s in Shop) == len(q.shop for q in p.shops.values()
                                               if q.quantity > 0))

# 7. ������, ��������� �� ���������� �������

select(o for o in Order if len(o.items) > 1)

# 8. ������������ ����

select(max(p.price for p in Product))

# 9. ����� ������� �����

select(p for p in Product if p.price == max(p.price for p in Product))

select(p for p in Product).orderby(lambda p: -p.price)[0]

# 10. �����, ��������� ������������ �������

select(p for p in Product
       if sum(i.price * i.quantity for i in p.orders.values()))
          == max(sum(i.price * i.quantity for p2 in Product
                                          for i in p2.orders.values()))

select(p, sum(i.price * i.quantity for i in OrderItem if i.product == p) for p in Product
       ).orderby(lambda p, profit: -profit)[0]
