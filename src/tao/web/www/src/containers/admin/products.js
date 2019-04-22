'use strict'

import React from 'react'
import axios from 'axios'
import { Input, Table, Icon, message, Popconfirm, Divider } from 'antd'
import { ProductForm,LabelForm } from "../../components/Form"
import Modal from "antd/lib/modal";


const { Search } = Input

export default class ProdcutsManager extends React.Component {
  constructor(props) {
    super(props)
    this.state = {visibleLabel: false, visibleProduct:false, editing_id: '', loading: true}
    this.total = 0
    this.limit = 10
    this.page = 1
    this.product = {}
    this.products = []
    this.qs = undefined
    this.columns = [
      {title: '名称', width: '20%', align: 'center', dataIndex: 'name', editable: true, key: 'name',
        render: (text, record) => (
          <span>
            <span>{text}&nbsp; &nbsp;</span>
            <a onClick={this.edit}><Icon  type="edit" /></a>
            <Divider type='vertical'/>
            <a onClick={this.delete}><Icon type="delete" /></a>
          </span>
        )},
      {title: '库存', width: '20%', align: 'center', dataIndex: 'stock', editable: true, key: 'stock'},
      {title: '价格', width: '20%', align: 'center', dataIndex: 'price', editable: true, key: 'price'},
      {title: (
          <span>
            <span>种类</span>
            <a onClick={this.handleAddLabel}><Icon  type="plus" /></a>
          </span>
        ), width: '20%', align: 'center', dataIndex: 'label', editable: true, key: 'label'},
      {
        title: (
          <span>
            <a href='javascript:void(0)' onClick={this.handleAddProduct}><Icon type='plus' /></a>
            <Search
              placeholder='输入名称进行筛选'
              onSearch={this.handleSearch}
              onChange={e => {
                if (e.target.value==='') {
                  this.handleSearch('')
                }
              }}
              allowClear={true}
              style={{width: '80%', marginLeft: '10%'}}
            />
          </span>
        ),
        align: 'center',
        dataIndex: '_add',
        key: '_add',
        render: (text, record) => (
         record.flag?(
           <span>
             <span>上架</span>
             <Divider type='vertical'/>
             <span><a onClick={this.loadStore}>下架</a></span>
           </span>
         ):(
           <span>
             <span><a onClick={this.downStore}>上架</a></span>
             <Divider type='vertical'/>
             <span>下架</span>
           </span>
         )
        )},
  ]
    this.intervalId = null
  }

  getProduct = async () => {
    let params = {
      skip: (this.page - 1) * this.limit,
      limit: this.limit,
    }
    await axios.get('/api/v1/all_products', )
      .then(resp => {
        this.total = resp.data.total
        this.products = resp.data.products
      })
      .catch(e => {
        message.error('加载prodcut列表失败！')
      })
  }

  async componentDidMount() {
    const reloadproduct = async () => {
      await this.getProduct();
      this.setState({loading: false});
      this.intervalId = setTimeout(reloadproduct, 10000) // reload tasks every 10 seconds
    };
    await reloadproduct()
  }

  componentWillUnmount() {
    if (this.intervalId) {
      clearTimeout(this.intervalId)
    }
  }

  loadStore = () => {
    console.log('上架')
  }

  downStore = () => {
    console.log('下架')
  }

  handleChange = async product => {
    // edit
    await axios.put('/api/v1/prodcut', product)
      .then(resp => {
        message.success('成功修改')
      })
      .catch(err => {
        message.error(`修改prodcut失败，错误：${err}`)
      })
  }

  handleDelete = async (_id) => {
    // delete
    const url = '/api/v1/product?_id=' + _id;
    await axios.delete(url)
      .then(resp => {
        message.success('成功删除prodcut配置')
      })
      .catch(err => {
        message.error(`删除prodcut错误：${err}`)
      })
  }

  save = (form, _id) => {
    form.validateFields((error, row) => {
      if (error) {
        return
      }
      const newData = [...this.products]
      const index = newData.findIndex(item => _id === item._id)
      const item = newData[index]
        newData.splice(index, 1, {
          ...item,
          ...row,
        })
      if (_id.length > 1) {
        this.handleChange(newData[index])
        this.getProduct().then(() =>{
                this.setState({ editing_id: '' })
              })
      }
    })
  }

  handleAddProduct = () =>{
    this.setState({visibleProduct:true})
  }
  handleCloseProduct =() =>{
    this.setState({visibleProduct:false})
  }

  handleSubmitProduct = async ()=>{
    this.handleCloseProduct()
    await this.getProduct()
  }

  handleAddLabel = () =>{
    this.setState({visibleLabel:true})
  }
  handleCloseLabel =() =>{
    this.setState({visibleLabel:false})
  }


  delete = _id => {
    const dataSource = this.prodcuts
    this.prodcuts = dataSource.filter(item => item._id !== _id)
    this.handleDelete(_id)
    this.getProdcut().then(() =>{
                this.setState({ editing_id: '' })
              })
  }

  add = () =>{
    this.setState({editvisibleProduct: true})
  }

  handleSearch = async (e) => {
    this.qs = e || undefined
    this.setState({loading: true})
    await this.getprodcut()
    this.setState({loading: false})
  }

  render() {
    const columns = this.columns.map((col) => {
      return {
        ...col,
        onCell: record => ({
          record,
          inputType: col.dataIndex === 'text',
          dataIndex: col.dataIndex,
          title: col.title,
        }),
      };
    });

    const {loading} = this.state

    return (
      <div>
        <Table
          loading={loading}
          columns={columns}
          dataSource={this.products}
          size='middle'
          rowKey='_id'
          pagination={{
            total: this.total,
            pageSize: this.limit,
            current: this.page,
            showTotal: total => `共 ${this.total} 个prodcut记录`,
            onChange: async (page, pageSize) => {
              this.page = page,
                this.total = pageSize,
                await this.getProduct(),
                this.setState({loading: false})
            }
          }}
        />
        <Modal
          title="添加商品"
          width={340}
          visible={this.state.visibleProduct}
          onCancel={this.handleCloseProduct}
          footer={null}
        >
          <ProductForm onSubmit={this.handleSubmitProduct}/>
        </Modal>
        <Modal
          title="添加分类"
          width={340}
          visible={this.state.visibleLabel}
          onCancel={this.handleCloseLabel}
          footer={null}>
          <LabelForm onSubmit={this.handleCloseLabel}/>
        </Modal>
      </div>
    )
  }}



