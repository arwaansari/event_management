from odoo.tools import date_utils
import json
import io

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

from odoo import models, fields


class EventReportWizard(models.TransientModel):
    _name = 'event.report.wizard'
    _description = 'Event Report Wizard'

    from_date = fields.Datetime()
    to_date = fields.Datetime()
    event_type_id = fields.Many2one('event.type', string='Event Type')
    current_date = fields.Date(default=fields.Date.today())
    include_catering = fields.Boolean()

    def print_pdf_report(self):
        query = """ 
        SELECT event_booking.id,event_booking.name,res_partner.name as customer,
        event_type.name as event_type,
        event_booking.booking_date,event_booking.state,
        sum(event_catering.grand_total) as total,
        event_catering.id as catering_id,
        substring(array_to_string(array_agg(event_catering.name),',') from 0 for 8) as catering,
        array_to_string(array_agg(event_catering_menu.name),',') as items,
        event_catering_menu.category,
        event_catering.welcome_drink,event_catering.breakfast,
        event_catering.lunch,event_catering.dinner,event_catering.snacks_and_drinks,
        event_catering.beverages
        FROM event_booking 
        INNER JOIN event_type 
        ON event_booking.type_id = event_type.id
        INNER JOIN res_partner
        ON event_booking.customer_id = res_partner.id
        INNER JOIN event_catering
        ON event_booking.id = event_catering.event_id
        INNER JOIN event_catering_page
        ON event_catering.id = event_catering_page.catering_wd_id
        OR event_catering.id = event_catering_page.catering_br_id
        OR event_catering.id = event_catering_page.catering_lu_id
        OR event_catering.id = event_catering_page.catering_sd_id
        OR event_catering.id = event_catering_page.catering_di_id
        OR event_catering.id = event_catering_page.catering_bv_id
        INNER JOIN event_catering_menu
        ON event_catering_page.item_id = event_catering_menu.id
        WHERE 1=1 
        """

        if self.event_type_id:
            query += """AND type_id = '%s' """ % self.event_type_id.id

        if self.from_date:
            query += """AND event_booking.start_date >= '%s' """ % \
                     self.from_date

        if self.to_date:
            query += """AND event_booking.end_date <= '%s' """ % self.to_date

        query += """GROUP BY event_catering.event_id,event_booking.name, 
        res_partner.name, event_type.name, event_booking.booking_date,
        event_booking.state,event_catering.id,event_catering.name, 
        event_catering.welcome_drink,event_catering.breakfast,
        event_catering.lunch,event_catering.dinner,
        event_catering.snacks_and_drinks,event_catering.beverages,
        event_catering_menu.category,event_booking.id
        ORDER BY event_booking.id"""

        cr = self._cr
        cr.execute(query)
        sql_dict = self._cr.dictfetchall()

        print(sql_dict)
        l = []
        dic = {}
        cat_id = []

        # pp=[]
        # l={'caterting':'sql_dict['catering']'}
        # print(l)
        event_id = []
        total = 0
        for rec in sql_dict:
            total += rec['total']
            # print(rec['catering'])
            l.append(rec['catering'])
            event_id.append(rec['id'])
            # cat_id.append(rec['catering_id'])
            # copy = [set(i.get('catering') for i in l)]
            # print(l)
            # print(copy)

            # for i in l:
            #     # print(copy, 'copy')
            #     for rec1 in sql_dict:
            #         if i == rec1['catering']:
            #             # print(i, '------------------')
            #             dic[i] = {rec1['category']: rec1['items']}
            #         d = {}
            #         for rec2 in dic:
            #             for rec3 in dic[rec2]:
            #                 d[rec3] = {}
            #                 # d[rec3] = tuple(d[rec3] for d in dic[rec2])
            #                 print(d)

            # print(dic[rec2])
            # dic[i] = {'category': rec['category'],
            #           'items': rec['items']}
            # if i in dic:
            #     dic[i].update(['items'])
            # print(dic)
            new_list = []
            for i in l:
                for j in event_id:
                    # print(copy, 'copy')
                    for rec1 in sql_dict:
                        # print(rec,'rec')
                        if i == rec1['catering'] and j == rec1['id']:
                            if j in dic:
                                dic[j] = dic[j], {rec1['catering']: {
                                    rec1['category']: rec1['items']}}
                                print(i, '------------------')
                            else:
                                dic[j] = {rec1['catering']: {
                                    rec1['category']: rec1['items']}}
                            #     dic[j].update({rec1['catering']: {rec1['category']: rec1['items']}})

                            # dic[i] = {'category': rec['category'],
                            #           'items': rec['items']}
                        # if i in dic:
                        #     dic[i].update(['items'])
                    print(dic)

                # if i['category']
                #     print('kkk')
                # else:
                #     print('dddd')

        # welcome_drink = []
        # breakfast = []
        # lunch = []
        # for rec in sql_dict:
        #     category = rec['category']
        #     if category == 'welcome_drink':
        #         welcome_drink.append(rec['items'])
        #     if category == 'breakfast':
        #         breakfast.append(rec['items'])
        #     if category == 'lunch':
        #         lunch.append(rec['items'])
        #
        # print(welcome_drink)

        data = {
            'event_type_id': self.event_type_id.name,
            'to_date': self.to_date,
            'from_date': self.from_date,
            'current_date': self.current_date,
            'include_catering': self.include_catering,
            'total': total,
            'sql_data': sql_dict
        }
        return self.env.ref(
            'event_management.action_report_event'). \
            report_action(None, data=data)

    def print_xlsx_report(self):
        query = """ 
        SELECT event_booking.name,res_partner.name as customer,
        event_type.name as event_type,
        event_booking.booking_date,event_booking.state,
        sum(event_catering.grand_total) as total,
        array_to_string(array_agg(event_catering.name),',') as catering
        FROM event_booking 
        INNER JOIN event_type 
        ON event_booking.type_id = event_type.id
        INNER JOIN res_partner
        ON event_booking.customer_id = res_partner.id
        INNER JOIN event_catering
        ON event_booking.id = event_catering.event_id
        WHERE 1=1 
        """

        if self.event_type_id:
            query += """AND type_id = '%s' """ % self.event_type_id.id

        if self.from_date:
            query += """AND event_booking.start_date >= '%s' """ % \
                     self.from_date

        if self.to_date:
            query += """AND event_booking.end_date <= '%s' """ % self.to_date

        query += """GROUP BY event_catering.event_id,event_booking.name,
        res_partner.name,event_type.name,event_booking.booking_date,
        event_booking.state"""

        cr = self._cr
        cr.execute(query)
        sql_dict = self._cr.dictfetchall()

        total = 0
        for rec in sql_dict:
            total += rec['total']

        data = {
            'event_type_id': self.event_type_id.name,
            'to_date': self.to_date,
            'from_date': self.from_date,
            'current_date': self.current_date,
            'include_catering': self.include_catering,
            'total': total,
            'sql_data': sql_dict
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'event.report.wizard',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Event Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        from_date = data['from_date']
        to_date = data['to_date']
        event_type_id = data['event_type_id']
        current_date = data['current_date']
        include_catering = data['include_catering']
        query = """ 
                SELECT event_booking.id,event_booking.name,res_partner.name as customer,
        event_type.name as event_type,
        event_booking.booking_date,event_booking.state,
        sum(event_catering.grand_total) as total,
        event_catering.name as catering,
        array_to_string(array_agg(event_catering_menu.name),',') as items,
        event_catering_page.unit_price, event_catering_page.quantity,
        event_catering_page.subtotal
        FROM event_booking 
        INNER JOIN event_type
        ON event_booking.type_id = event_type.id
        INNER JOIN res_partner
        ON event_booking.customer_id = res_partner.id
        INNER JOIN event_catering
        ON event_booking.id = event_catering.event_id
        INNER JOIN event_catering_page
        ON event_catering.id = event_catering_page.catering_wd_id
        OR event_catering.id = event_catering_page.catering_br_id
        OR event_catering.id = event_catering_page.catering_lu_id
        OR event_catering.id = event_catering_page.catering_sd_id
        OR event_catering.id = event_catering_page.catering_di_id
        OR event_catering.id = event_catering_page.catering_bv_id
        INNER JOIN event_catering_menu
        ON event_catering_page.item_id = event_catering_menu.id
        WHERE 1=1 
        """

        if event_type_id:
            query += """AND event_type.name = '%s' """ % event_type_id

        if from_date:
            query += """AND event_booking.start_date >= '%s' """ % \
                     from_date

        if to_date:
            query += """AND event_booking.end_date <= '%s' """ % to_date

        query += """GROUP BY event_catering.event_id,event_booking.name,
        res_partner.name,event_type.name,event_booking.booking_date,
        event_booking.state,event_catering.name,event_catering_page.unit_price,
        event_catering_page.quantity,event_catering_page.subtotal,event_booking.id"""
        cr = self._cr
        cr.execute(query)
        sql_dict = self._cr.dictfetchall()

        catering_list = []
        dic = {}
        event_id = []
        total = 0
        for rec in sql_dict:
            total += rec['total']
            catering_list.append(rec['catering'])
            event_id.append(rec['id'])

        for i in catering_list:
            # for j in event_id:
            # print(copy, 'copy')
            for rec1 in sql_dict:
                # print(rec,'rec')
                if not dic.get(i, False):
                    if i == rec1['catering']:
                        dic[i] = [{
                            'item': rec1['items'],
                            'unit_price': rec1['unit_price'],
                            'quantity': rec1['quantity'],
                            'subtotal': rec1['subtotal']
                        }]
                        # print(i, '------------------')
                    else:
                        if i == rec1['catering']:
                            dic[i].append({
                                'item': rec1['items'],
                                'unit_price': rec1['unit_price'],
                                'quantity': rec1['quantity'],
                                'subtotal': rec1['subtotal']
                            })

                    print(dic)
        # print(sql_dict)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center'})
        header = workbook.add_format({'bold': True, 'align': 'center'})
        header_style = workbook.add_format({'bold': True})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
        row = 4
        if from_date:
            sheet.write(row, 0, 'From Date:' + from_date, header_style)
            # sheet.write(row, 2, from_date, cell_format)
            row += 1
            if to_date:
                sheet.write(row, 0, 'To date:' + to_date, header_style)

                row += 1
        else:
            sheet.write(row, 0, 'Date:' + current_date, header_style)
            row += 1
        if event_type_id:
            sheet.write(row, 0, 'Event Type:' + event_type_id, header_style)
            row += 1
        row += 1
        column = 0
        sheet.write(row, column, 'Sl.no', header)
        column += 1
        sheet.write(row, column, 'Event', header)
        column += 1
        if not event_type_id:
            sheet.write(row, column, 'Event Type', header)
            column += 1
        sheet.write(row, column, 'Customer', header)
        column += 1
        sheet.write(row, column, 'Booking Date', header)
        column += 1
        sheet.write(row, column, 'Status', header)
        column += 1
        sheet.write(row, column, 'Amount', header)
        column += 1
        # if include_catering:
        #     sheet.write(row, column, 'Catering', header)
        #     column += 1
        #     sheet.write(row, column, 'Items', header)
        #     column += 1

        head_column = column
        if head_column == 6:
            sheet.merge_range('A2:F3', 'EVENT REPORT', head)
        if head_column == 7:
            sheet.merge_range('A2:G3', 'EVENT REPORT', head)
        if head_column == 8:
            sheet.merge_range('A2:H3', 'EVENT REPORT', head)
        sheet.set_column(1, 1, 60)
        sheet.set_column(2, 2, 15)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 20)

        row += 1
        number = 1
        for i in sql_dict:
            sheet.write(row, 0, number)
            sheet.write(row, 1, i['name'])
            if not event_type_id:
                sheet.write(row, 2, i['event_type'])
                sheet.write(row, 3, i['customer'])
                sheet.write(row, 4, str(i['booking_date']))
                sheet.write(row, 5, i['state'])
                sheet.write(row, 6, i['total'])
                if include_catering:
                    row += 1
                    sheet.write(row, 1, 'Catering', cell_format)
                    column += 1
                    sheet.write(row, 2, 'Items', cell_format)
                    column += 1
                    sheet.write(row, 3, 'Unit Price', cell_format)
                    column += 1
                    sheet.write(row, 4, 'Quantity', cell_format)
                    column += 1
                    sheet.write(row, 5, 'Subtotal', cell_format)
                    column += 1
                    row += 1
                    sheet.write(row, 1, i['catering'])
                    sheet.write(row, 2, i['items'])
                    sheet.write(row, 3, i['unit_price'])
                    sheet.write(row, 4, i['quantity'])
                    sheet.write(row, 5, i['subtotal'])

            else:
                sheet.write(row, 2, i['customer'])
                sheet.write(row, 3, str(i['booking_date']))
                sheet.write(row, 4, i['state'])
                sheet.write(row, 5, i['total'])
                if include_catering:
                    sheet.write(row, 6, i['catering'])
                    sheet.write(row, 7, i['items'])
            number += 1
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
