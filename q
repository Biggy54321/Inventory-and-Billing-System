[1mdiff --cc CmsLib/PySql.py[m
[1mindex 7ac69ed,633f0f5..0000000[m
[1m--- a/CmsLib/PySql.py[m
[1m+++ b/CmsLib/PySql.py[m
[36m@@@ -13,7 -13,7 +13,11 @@@[m [mclass PySql[m
      def __init__(self, flask_app, path_to_yaml):[m
  [m
          # Load the yaml file[m
[32m++<<<<<<< HEAD[m
[32m +        db_details = yaml.load(open(path_to_yaml), Loader=yaml.FullLoader)[m
[32m++=======[m
[32m+         db_details = yaml.load(open(path_to_yaml), Loader = yaml.FullLoader)[m
[32m++>>>>>>> 55e7513db0bd4ddde42977b92533ad7cc8cf4591[m
  [m
          # Configure the flask object[m
          flask_app.config['MYSQL_HOST'] = db_details['mysql_host'][m
