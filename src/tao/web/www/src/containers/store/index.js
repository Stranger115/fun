'use strict'

import React from 'react'
import 'antd/dist/antd.css';
import {Carousel, Card, Divider, Tag, Pagination, Button, Table, message} from 'antd'
import {Sorts, Products} from '../../externals'
import styles from './index.css';
import ads from '../../static/ads.jpg'
import logo from '../../static/logo.png'
import {Menu} from "antd/lib/menu";
import {PageNumSessionKey} from "../../constants";
import {getSearchParams} from "../../utils";
import axios from "axios";

const onChangeShowProcucts = (current, pageSize) =>{
  console.log(current, pageSize);
};
const onShowSizeChange = (current, pageSize) =>{

};

export default class Store extends React.Component {
  constructor(props) {
    super(props)
    this.products = Products;
    this.value = this.init();
    this.state = { editVisible:false, editing_id: '', loading: true, data:this.value}
    this.total = Products.length*4;
    this.limit = 4;
    this.page = 1;
    this.value = 0;
    this.columns = [{
      dataIndex: 'product',
      key: 'product',
      render: (text, record) => (
        <div>
        {
          record.map((e, idx) =>
            <span key={idx}>
              <Card className={styles.card}
                    cover={<img src={ads}/>}
              >
                <p>{e.title}</p>
                <Button shape="circle" icon="minus" onClick={this.handleSub.bind(this, event, e.title)}/>
                <strong>{this.state.data[e.title]}</strong>
                <Button shape="circle" onClick={this.handleAdd.bind(this, event, e.title, e.value)} icon="plus"/>
                <Button style={{float: 'right'}} shape="circle" icon="shopping-cart"/>
              </Card>
            </span>
          )
        }
        </div>
      )
    }];
  }

  init = ()=>{
    let value = {};
    for(let i in this.products){
      for(let j in this.products[i]){
        value[this.products[i][j].title] = 0;
      }
    }
    return value
  };
  handleChange= (title, value)=>{
    let count = this.state.data;
    count[title] = value;
    this.setState({data:count});
    console.log(this.state.data)
  };

  handleAdd = (event,value, title) => {
    let old = this.state.data[title];
    if(old<value){
      old ++;
      this.handleChange(title, old)
    }
    else{
       alert('库存不足仅有%s件商品'%value)
    }
  };
  handleSub = (event, title)=>{
    let value = this.state.data[title];
    if(value>0){
      value --;
      this.handleChange(title, value)
    }
  };
  async loadStores() {
    console.log(1)
  }

  render() {
    const {loading} = this.state.loading
    return (
      <div>
        <Carousel autoplay>
          <div><img src={ads} /></div>
          <div><img src={logo} /></div>
          <div><img src={ads} /></div>
          <div><img src={logo} /></div>
        </Carousel>
        <div style={{ background: 'rgb(190, 200, 200)', padding: '26px 16px 16px' }}>
        {
          Sorts.map((e, idx) =>
              <span key={idx} >
                <Tag color="volcano">{e}</Tag>
                <Divider type="vertical"/>
              </span>
            )
        }
        </div>
        <Table
          showHeader={false}
          columns={this.columns}
          dataSource={this.products}
          loading={false}    //{loading}
          rowKey='_id'
          pagination={{
            total: this.total,
            pageSize: this.limit,
            current: this.page,
            onChange: async (page, pageSize) => {
              this.page = page
              sessionStorage.setItem(PageNumSessionKey, page)
              this.total = pageSize
              this.setState({loading: true})
              await this.loadStores()
              this.setState({loading: false})
            },
            showTotal: total => `共 ${total}个商品`
          }}
        />
      </div>
    )
  }
}
