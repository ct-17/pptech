from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = ["product.template"]

    short_description = fields.Html('Short Description')


class ProductCategoryInherit(models.Model):
    _inherit = "product.category"

    """
    cig_categ_sql = "select id, name from product_category order by name"
    cur.execute(cig_categ_sql)
    cig_categ = cur.fetchall()

    public_cig_categ_sql = "select id, name from product_public_category order by name"
    cur.execute(public_cig_categ_sql)
    public_cig_categ = cur.fetchall()

    for pc_tup in cig_categ:
        for ppc_tup in public_cig_categ:
            if pc_tup[1] == ppc_tup[1]:
                sql = "update product_category set public_categ_id = {public_id} where id = {pc_id}"\
                .format(
                    public_id=ppc_tup[0],
                    pc_id=pc_tup[0]
                )
                cur.execute(sql)
                conn.commit()
                
    need to run sql populate script similar to above to manually populate public_categ_id
    """
    public_categ_id = fields.Many2one('product.public.category', 'Public Category')