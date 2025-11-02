import React, { useState } from 'react';
import { Button, Modal, Input } from 'antd';
import { stocksAPI } from '../../services';
import './AddStock.scss';

function AddStock() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [stockCode, setStockCode] = useState('');

  const showModal = () => {
    setIsModalOpen(true);
  };

  const handleOk = () => {
    setIsModalOpen(false);
    handleAddStock();
    console.log('api confirm clicked.');
  };

  const handleCancel = () => {
    setStockCode('');
    setIsModalOpen(false);
  };

  const handleAddStock = async () => {
    try {
      await stocksAPI.addStock({ code: stockCode });
    } catch (error) {
      console.error('Failed to add stock:', error);
    }
  };

  return (
    <div>
      <Button color='purple' size='small' variant='outlined' onClick={showModal}>
        添加股票
      </Button>
      <Modal
        title='添加股票'
        className='add-stock-modal'
        closable={{ 'aria-label': 'Custom Close Button' }}
        open={isModalOpen}
        onOk={handleOk}
        onCancel={handleCancel}>
        <p>请输入股票代码: </p>
        <Input
          placeholder='例如: AAPL, 000001.SZ'
          value={stockCode}
          onChange={e => setStockCode(e.target.value)}
        />
      </Modal>
    </div>
  );
}

export default AddStock;
