import React from 'react'
import Store from './containers/store'
import {ProdcutsManager, CherkManager, UserManager, RoleManager } from './containers/admin'


export default [
  {
    name: '商品列表',
    url: '/store',
    icon: 'shopping-cart',
    component: Store,
    inMenu: true,
    role:0x00,
    subMenu:null,
  },
  {
    name: '管理模块',
    url: '/admin',
    icon: 'schedule',
    component: null,
    inMenu: true,
    role: 0,//0xff,
    subMenu:[
      {
        name: '会员管理',
        url: '/UserManager',
        icon: 'shopping-cart',
        component: UserManager,
        inMenu: true,
        role:0x00,
      },
      {
        name: '权限管理',
        url: '/RoleManager',
        icon: 'shopping-cart',
        component: RoleManager,
        inMenu: true,
        role:0x00,
      },
      {
        name: '商品管理',
        url: '/ProdcutsManager',
        icon: 'shopping-cart',
        component: ProdcutsManager,
        inMenu: true,
        role:0x00,
      },
      {
        name: '账单管理',
        url: '/CherkManager',
        icon: 'shopping-cart',
        component: CherkManager,
        inMenu: true,
        role:0x00,
      }
    ],
  }
]
